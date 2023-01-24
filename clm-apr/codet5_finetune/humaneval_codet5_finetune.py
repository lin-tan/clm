import codecs
import json
import os
import sys
import torch
import numpy as np
import subprocess
import time
from transformers import RobertaTokenizer, T5ForConditionalGeneration

CODET5_FINETUNE_DIR = os.path.abspath(__file__)[: os.path.abspath(__file__).rindex('/') + 1]
JAVA_DIR = CODET5_FINETUNE_DIR + '../../jasper/'

def command(cmd):
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output, err = process.communicate()
    if output != b'' or err != b'':
        print(output)
        print(err)
    return output, err

def get_codet5_finetune_input(buggy_file, rem_start, rem_end, tmp_file):
    os.chdir(JAVA_DIR)
    command([
        'java', '-cp', '.:target:lib/*', 'clm.finetuning.FineTuningData', 'inference',
        buggy_file, str(rem_start), str(rem_end), tmp_file
    ])

def humaneval_codet5_finetune_input(output_file, humaneval_dir):
    loc_fp = codecs.open(CODET5_FINETUNE_DIR + '../humaneval/humaneval_loc.txt', 'r', 'utf-8')
    codet5_input = {'config': 'finetune', 'data': {}}
    for line in loc_fp.readlines():
        filename, rem_loc = line.strip().split()
        start, end = rem_loc.split('-')
        end = str(int(end) - 1) if end != start else end
        tmp_file = CODET5_FINETUNE_DIR + '../humaneval/tmp.json'
        get_codet5_finetune_input(humaneval_dir + 'src/main/java/humaneval/buggy/' + filename + '.java', start, end, tmp_file)
        
        if not os.path.exists(tmp_file):
            print(filename, 'failed.', tmp_file, 'not found.')
        print(filename, 'succeeded')

        result = json.load(open(tmp_file, 'r'))
        codet5_input['data'][filename] = {
            'loc': rem_loc,
            'input': result["buggy function before"] + "</s>" + result["buggy line"] + "</s>" + result["buggy function after"],
        }
        command(['rm', '-rf', tmp_file])
    json.dump(codet5_input, open(output_file, 'w'), indent=2)


def humaneval_codet5_finetune_output(input_file, output_file, model_dir, model_name, num_output=10):
    tokenizer = RobertaTokenizer.from_pretrained(model_dir + model_name[:-9])
    model = T5ForConditionalGeneration.from_pretrained(model_dir + model_name).to(device_id)
    
    codet5_output = json.load(open(input_file, 'r'))
    codet5_output['model'] = model_name
    starter, ender = torch.cuda.Event(enable_timing=True), torch.cuda.Event(enable_timing=True)
    timings = []
    memory_allocated, memory_reserved = 0, 0
    for i, filename in enumerate(codet5_output['data']):
        text = codet5_output['data'][filename]['input']

        print(i + 1, 'generating', filename)

        input_ids = tokenizer(text, return_tensors="pt").input_ids.to(device_id)
        eos_id = tokenizer.convert_tokens_to_ids(tokenizer.eos_token)
        starter.record()
        generated_ids = model.generate(
            input_ids, max_new_tokens=64, num_beams=10, num_return_sequences=num_output, early_stopping=True, 
            pad_token_id=eos_id, eos_token_id=eos_id
        )
        ender.record()
        torch.cuda.synchronize()
        curr_time = starter.elapsed_time(ender)
        timings.append(curr_time)
        
        if torch.cuda.memory_allocated(device_id) / (1024 * 1024) > memory_allocated:
            memory_allocated = torch.cuda.memory_allocated(device_id) / (1024 * 1024)
        if torch.cuda.memory_reserved(device_id) / (1024 * 1024) > memory_reserved:
            memory_reserved = torch.cuda.memory_reserved(device_id) / (1024 * 1024)

        print(curr_time, memory_allocated, memory_reserved)
        output = []
        for generated_id in generated_ids:
            output.append(tokenizer.decode(generated_id, skip_special_tokens=True))
        codet5_output['data'][filename]['output'] = output
        json.dump(codet5_output, open(output_file, 'w'), indent=2)
    
    codet5_output['time'] = int(np.sum(timings) / 1000)
    codet5_output['memory_allocated'] = memory_allocated
    codet5_output['memory_reserved'] = memory_reserved
    json.dump(codet5_output, open(output_file, 'w'), indent=2)


if __name__ == '__main__':
    device_id = 0   # need one GPU with 12GB memory (CPU is also ok)
    model_dir = sys.argv[1]
    humaneval_dir = CODET5_FINETUNE_DIR + '../../humaneval-java/'
    
    input_file = CODET5_FINETUNE_DIR + '../humaneval/codet5_finetune_result/codet5_input.json'
    print("==========Preparing input of HumanEval benchmark to finetuned CODET5 model==========")
    humaneval_codet5_finetune_input(input_file, humaneval_dir=humaneval_dir)
    print("==========Input written to " + input_file)
    
    for model_name in ('codet5-small-finetune', 'codet5-base-finetune', 'codet5-large-finetune'):
        output_file = CODET5_FINETUNE_DIR + '../humaneval/codet5_finetune_result/' + '_'.join(model_name.split('-')[:-1]) + '_output.json'
        print("==========Generating output of HumanEval benchmark by " + model_name + "==========")
        humaneval_codet5_finetune_output(input_file, output_file, model_dir, model_name, num_output=10)
        print("==========Output written to " + output_file)
