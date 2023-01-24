import codecs
import json
import sys
import os
import re
import subprocess
from codegen_config import CodeGenInputConfig
from transformers import AutoTokenizer, AutoModelForCausalLM

CODEGEN_DIR = os.path.abspath(__file__)[: os.path.abspath(__file__).rindex('/') + 1]
JAVA_DIR = CODEGEN_DIR + '../../jasper/'

def command(cmd):
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output, err = process.communicate()
    if output != b'' or err != b'':
        print(output)
        print(err)
    return output, err

def get_codegen_input(filename, start, end, config, tmp_file):
    os.chdir(JAVA_DIR)
    command([
        'java', '-cp', '.:target:lib/*', 'clm.codegen.CodeT5InputParser',
        filename, start, end, config, tmp_file
    ])

def defects4j_codegen_input(config, output_file, tmp_dir):
    loc_fp = codecs.open(CODEGEN_DIR + '../defects4j/defects4j_loc.txt', 'r', 'utf-8')
    codegen_input = {'config': config, 'data': {}}
    for line in loc_fp.readlines():
        proj, bug_id, path, rem_loc, add_loc = line.strip().split()
        start, end = rem_loc.split('-')
        end = str(int(end) - 1) if end != start else end
        tmp_file = CODEGEN_DIR + '../defects4j/tmp.json'

        subprocess.run(['defects4j', 'checkout', '-p', proj, '-v', bug_id + 'b', '-w', tmp_dir], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        get_codegen_input(tmp_dir + path, start, end, config, tmp_file)
        
        if not os.path.exists(tmp_file):
            print(proj, bug_id, 'failed.', tmp_file, 'not found.')
            continue
        print(proj, bug_id, 'succeeded')

        result = json.load(open(tmp_file, 'r'))
        if result['input'].strip() == '':
            print(proj, bug_id, 'failed. all empty.')
            continue
        
        result = json.load(open(tmp_file, 'r'))
        codegen_input['data'][filename] = {
            'loc': rem_loc,
            'input': result['input'],
            'function range': result['function range']
        }

        command(['rm', '-rf', tmp_file])
        command(['rm', '-rf', tmp_dir])
        json.dump(codegen_input, open(output_file, 'w'), indent=2)

def defects4j_codegen_output(input_file, output_file, model_dir, model_name, num_output=10):
    codegen_output = json.load(open(input_file, 'r'))
    codegen_output['model'] = model_name
    tokenizer = AutoTokenizer.from_pretrained(model_dir + model_name)
    model = AutoModelForCausalLM.from_pretrained(model_dir + model_name)
    model.parallelize(device_map)
    
    for filename in codegen_output['data']:
        text = codegen_output['data'][filename]['input']

        print('generating', filename)
        
        try:
            input_ids = tokenizer(text, return_tensors="pt").input_ids.to(device_ids[0])
            if input_ids.size(1) >= 768:
                print('input too long:', input_ids.size(1), 'skip')
                continue

            eos_id = tokenizer.convert_tokens_to_ids(tokenizer.eos_token)
            generated_ids = model.generate(
                input_ids, max_new_tokens=512, num_beams=num_output, num_return_sequences=num_output, early_stopping=True,
                pad_token_id=eos_id, eos_token_id=eos_id
            )
            output = []
            for generated_id in generated_ids:
                output.append(tokenizer.decode(generated_id, skip_special_tokens=True))
        except Exception as e:
            output = []
            
        codegen_output['data'][filename]['output'] = output
        json.dump(codegen_output, open(output_file, 'w'), indent=2)


if __name__ == '__main__':
    model_dir = sys.argv[1]
    for i, config in enumerate(CodeGenInputConfig):
        input_file = CODEGEN_DIR + '../defects4j/codegen_result/codegen_input_c' + str(i + 1) + '.json'
        
        print("==========Preparing input of Defects4J benchmark to CODEGEN model, Config: " + config + "==========")
        defects4j_codegen_input(config, input_file, tmp_dir='/tmp/codegen/')
        print("==========Input written to " + input_file)
        
        for model_name in ('codegen-350M', 'codegen-2B', 'codegen-6B'):
            if model_name == 'codegen-350M':
                device_map = {
                    0: [_ for _ in range(0, 20)]
                }
                device_ids = list(device_map.keys())    # need one GPU with 12GB memory to run codegen-350M
            elif model_name == 'codegen-2B':
                device_map = {
                    0: [_ for _ in range(0, 7)],
                    1: [_ for _ in range(7, 16)],
                    2: [_ for _ in range(16, 25)],
                    3: [_ for _ in range(25, 32)]
                }
                device_ids = list(device_map.keys())    # need 4 GPUs with 4*12 GB memory in total to run codegen-2B
            else:
                device_map = {
                    0: [_ for _ in range(0, 4)], 
                    1: [_ for _ in range(4, 8)],
                    2: [_ for _ in range(8, 12)],
                    3: [_ for _ in range(12, 16)],
                    4: [_ for _ in range(16, 20)],
                    5: [_ for _ in range(20, 24)],
                    6: [_ for _ in range(24, 29)],
                    7: [_ for _ in range(29, 33)]
                }
                device_ids = list(device_map.keys())    # need 8 GPUs with 8*12 GB memory in total to run codegen-6B 
                                                        # (the author use 4 A5000 GPUs with 4*24 GB memory to run)
            
            output_file = CODEGEN_DIR + '../defects4j/codegen_result/' + '_'.join(model_name.split('-')) + '_output_c' + str(i + 1) + '.json'
            # model_dir = CODEGEN_DIR + '../models/'
            print("==========Generating output of Defects4J benchmark by " + model_name + ", Config: " + config + "==========")
            defects4j_codegen_output(input_file, output_file, model_dir, model_name)
            print("==========Output written to " + output_file)
