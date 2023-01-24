import codecs
import json
import sys
import os
import subprocess
import time
from codet5_config import CodeT5InputConfig
from transformers import RobertaTokenizer, T5ForConditionalGeneration

CODET5_DIR = os.path.abspath(__file__)[: os.path.abspath(__file__).rindex('/') + 1]
JAVA_DIR = CODET5_DIR + '../../jasper/'

def command(cmd):
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output, err = process.communicate()
    if output != b'' or err != b'':
        print(output)
        print(err)
    return output, err

def get_codet5_input(filename, start, end, config, tmp_file):
    os.chdir(JAVA_DIR)
    command([
        'java', '-cp', '.:target:lib/*', 'clm.codet5.CodeT5InputParser',
        filename, start, end, config, tmp_file
    ])

def humaneval_codet5_input(config, output_file, humaneval_dir):
    loc_fp = codecs.open(CODET5_DIR + '../humaneval/humaneval_loc.txt', 'r', 'utf-8')
    codet5_input = {'config': config, 'data': {}}
    for line in loc_fp.readlines():
        filename, rem_loc = line.strip().split()
        start, end = rem_loc.split('-')
        end = str(int(end) - 1) if end != start else end
        tmp_file = CODET5_DIR + '../humaneval/tmp.json'
        get_codet5_input(humaneval_dir + 'src/main/java/humaneval/buggy/' + filename + '.java', start, end, config, tmp_file)
        
        if not os.path.exists(tmp_file):
            print(filename, 'failed.', tmp_file, 'not found.')
        print(filename, 'succeeded')

        result = json.load(open(tmp_file, 'r'))
        codet5_input['data'][filename] = {
            'loc': rem_loc,
            'input': result['input'],
            'function range': result['function range']
        }
        command(['rm', '-rf', tmp_file])
    json.dump(codet5_input, open(output_file, 'w'), indent=2)


def humaneval_codet5_output(input_file, output_file, model_dir, model_name, num_output=10):
    codet5_output = json.load(open(input_file, 'r'))
    if codet5_output['config'] in ['CODET5_BASE_CODEFORM_MASKFORM_NOCOMMENT', 'CODET5_BASE_CODEFORM_COMMENTFORM_NOCOMMENT']:
        codet5_output['model'] = model_name
        tokenizer = RobertaTokenizer.from_pretrained(model_dir + model_name)
        model = T5ForConditionalGeneration.from_pretrained(model_dir + model_name).to(device_id)
    else:
        assert False, 'unrecognized config'
    start_time = time.time()
    for i, filename in enumerate(codet5_output['data']):
        text = codet5_output['data'][filename]['input']

        print(i + 1, 'generating', filename)

        input_ids = tokenizer(text, return_tensors="pt").input_ids.to(device_id)
        eos_id = tokenizer.convert_tokens_to_ids(tokenizer.eos_token)
        generated_ids = model.generate(input_ids, max_new_tokens=64, num_beams=10, num_return_sequences=num_output, early_stopping=True, eos_token_id=eos_id)
        output = []
        for generated_id in generated_ids:
            output.append(tokenizer.decode(generated_id, skip_special_tokens=True))
        codet5_output['data'][filename]['output'] = output
        json.dump(codet5_output, open(output_file, 'w'), indent=2)
    total_time = int(time.time() - start_time)
    codet5_output['time'] = total_time
    json.dump(codet5_output, open(output_file, 'w'), indent=2)


if __name__ == '__main__':
    device_id = 0   # need one GPU with 12GB memory (CPU is also ok)
    model_dir = sys.argv[1]
    humaneval_dir = CODET5_DIR + '../../humaneval-java/'
    for i, config in enumerate(CodeT5InputConfig):
        if config == 'CODET5_REFINE_CODEFORM_NOCOMMENT':
            continue
        
        input_file = CODET5_DIR + '../humaneval/codet5_result/codet5_input_c' + str(i + 1) + '.json'
        print("==========Preparing input of HumanEval benchmark to CODET5 model, Config: " + config + "==========")
        humaneval_codet5_input(config, input_file, humaneval_dir=humaneval_dir)
        print("==========Input written to " + input_file)
        
        for model_name in ('codet5-small', 'codet5-base', 'codet5-large'):
            output_file = CODET5_DIR + '../humaneval/codet5_result/' + '_'.join(model_name.split('-')) + '_output_c' + str(i + 1) + '.json'
            # model_dir = CODET5_DIR + '../models/'
            print("==========Generating output of HumanEval benchmark by " + model_name + ", Config: " + config + "==========")
            humaneval_codet5_output(input_file, output_file, model_dir, model_name)
            print("==========Output written to " + output_file)
