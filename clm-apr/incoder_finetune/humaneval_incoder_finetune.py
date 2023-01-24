import codecs
import os
import sys
import json
import time
import torch
import numpy as np
import subprocess
from transformers import AutoTokenizer, AutoModelForCausalLM

INCODER_FINETUNE_DIR = os.path.abspath(__file__)[: os.path.abspath(__file__).rindex('/') + 1]
JAVA_DIR = INCODER_FINETUNE_DIR + '../../jasper/'

def command(cmd):
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output, err = process.communicate()
    if output != b'' or err != b'':
        print(output)
        print(err)
    return output, err

def get_incoder_finetune_input(buggy_file, rem_start, rem_end, tmp_file):
    os.chdir(JAVA_DIR)
    command([
        'java', '-cp', '.:target:lib/*', 'clm.finetuning.FineTuningData', 'inference',
        buggy_file, str(rem_start), str(rem_end), tmp_file
    ])

def humaneval_incoder_finetune_input(output_file, humaneval_dir):
    loc_fp = codecs.open(INCODER_FINETUNE_DIR + '../humaneval/humaneval_loc.txt', 'r', 'utf-8')
    incoder_input = {'config': 'finetune', 'data': {}}
    for line in loc_fp.readlines():
        filename, rem_loc = line.strip().split()
        start, end = rem_loc.split('-')
        end = str(int(end) - 1) if end != start else end
        tmp_file = INCODER_FINETUNE_DIR + '../humaneval/tmp.json'
        get_incoder_finetune_input(humaneval_dir + 'src/main/java/humaneval/buggy/' + filename + '.java', start, end, tmp_file)
        
        if not os.path.exists(tmp_file):
            print(filename, 'failed.', output_file, 'not found.')
        print(filename, 'succeeded')

        result = json.load(open(tmp_file, 'r'))
        incoder_input['data'][filename] = {
            'loc': rem_loc,
            'input': result['buggy function before'] + '// buggy lines start:\n' + result['buggy line'] + '// buggy lines end:\n' + result['buggy function after'] + '// fixed lines:\n',
        }
        command(['rm', '-rf', tmp_file])
    json.dump(incoder_input, open(output_file, 'w'), indent=2)


def humaneval_incoder_finetune_output(input_file, output_file, model_dir, model_name, num_output=10):
    tokenizer = AutoTokenizer.from_pretrained(model_dir + model_name[:-9])
    model = AutoModelForCausalLM.from_pretrained(model_dir + model_name)
    model.parallelize(device_map)
    
    incoder_output = json.load(open(input_file, 'r'))
    incoder_output['model'] = model_name
    starter, ender = torch.cuda.Event(enable_timing=True), torch.cuda.Event(enable_timing=True)
    timings = []
    oom = 0
    memory_allocated, memory_reserved = 0, 0
    for i, filename in enumerate(incoder_output['data']):
        text = incoder_output['data'][filename]['input']

        print(i + 1, 'generating', filename)

        input_ids = tokenizer(text, return_tensors="pt").input_ids.to(device_ids[0])
        starter.record()
        try:
            eos_id = tokenizer.convert_tokens_to_ids('<|endofmask|>')
            generated_ids = model.generate(
                input_ids, max_new_tokens=128, num_beams=num_output, num_return_sequences=num_output, early_stopping=True,
                pad_token_id=eos_id, eos_token_id=eos_id
            )
        except Exception as e:
            oom += 1
            continue
        ender.record()
        torch.cuda.synchronize()
        curr_time = starter.elapsed_time(ender)
        timings.append(curr_time)
        
        total_allocated, total_reserved = 0, 0
        for device in device_ids:
            total_allocated += torch.cuda.memory_allocated(device) / (1024 * 1024)
            total_reserved += torch.cuda.memory_reserved(device) / (1024 * 1024)
        if total_allocated > memory_allocated:
            memory_allocated = total_allocated
        if total_reserved > memory_reserved:
            memory_reserved = total_reserved

        print(curr_time, memory_allocated, memory_reserved, oom)

        output = []
        for generated_id in generated_ids:
            output.append(tokenizer.decode(generated_id, skip_special_tokens=False))
        incoder_output['data'][filename]['output'] = output
        json.dump(incoder_output, open(output_file, 'w'), indent=2)
    # incoder_output['time'] = int(np.sum(timings) / 1000)
    # incoder_output['memory_allocated'] = memory_allocated
    # incoder_output['memory_reserved'] = memory_reserved
    json.dump(incoder_output, open(output_file, 'w'), indent=2)


if __name__ == '__main__':
    model_dir = sys.argv[1]
    humaneval_dir = INCODER_FINETUNE_DIR + '../../humaneval-java/'
    
    input_file = INCODER_FINETUNE_DIR + '../humaneval/incoder_finetune_result/incoder_input.json'
    print("==========Preparing input of HumanEval benchmark to finetuned INCODER model==========")
    humaneval_incoder_finetune_input(input_file, humaneval_dir=humaneval_dir)
    print("==========Input written to " + input_file)

    for model_name in ('incoder-1B-finetune', 'incoder-6B-finetune'):
        if model_name == 'incoder-1B-finetune':
            device_map = {
                0: [_ for _ in range(0, 5)],
                1: [_ for _ in range(5, 12)],
                2: [_ for _ in range(12, 19)],
                3: [_ for _ in range(19, 24)]
            }
            device_ids = list(device_map.keys())    # need 4 GPUs with 4*12 GB memory in total to run incoder-1B
        else:
            device_map = {
                0: [_ for _ in range(0, 4)], 
                1: [_ for _ in range(4, 8)],
                2: [_ for _ in range(8, 12)],
                3: [_ for _ in range(12, 16)],
                4: [_ for _ in range(16, 20)],
                5: [_ for _ in range(20, 24)],
                6: [_ for _ in range(24, 28)],
                7: [_ for _ in range(28, 32)]
            }
            device_ids = list(device_map.keys())    # need 8 GPUs with 8*12 GB memory in total to run incoder-6B 
                                                    # (the author use 4 A5000 GPUs with 4*24 GB memory to run)
        output_file = INCODER_FINETUNE_DIR + '../humaneval/incoder_finetune_result/' + '_'.join(model_name.split('-')[:-1]) + '_output.json'
        print("==========Generating output of HumanEval benchmark by " + model_name + "==========")
        humaneval_incoder_finetune_output(input_file, output_file, model_name, num_output=10)
        print("==========Output written to " + output_file)
