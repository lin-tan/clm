import os
import sys
import json
import codecs
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
        'java', '-cp', '.:target:lib/*', 'clm.codegen.CodeGenInputParser',
        filename, start, end, config, tmp_file
    ])


def quixbugs_codegen_input(config, output_file):
    loc_fp = codecs.open(CODEGEN_DIR + '../quixbugs/quixbugs_loc.txt', 'r', 'utf-8')
    codegen_input = {'config': config, 'data': {}}
    for line in loc_fp.readlines():
        filename, rem_loc, add_loc = line.strip().split()
        start, end = rem_loc.split('-')
        end = str(int(end) - 1) if end != start else end
        tmp_file = CODEGEN_DIR + '../quixbugs/tmp.json'
        get_codegen_input(CODEGEN_DIR + '../quixbugs/java_programs/' + filename + '.java', start, end, config, tmp_file)
        
        if not os.path.exists(tmp_file):
            print(filename, 'failed.', output_file, 'not found.')
        print(filename, 'succeeded')

        result = json.load(open(tmp_file, 'r'))
        codegen_input['data'][filename] = {
            'loc': rem_loc,
            'input': result['input'],
            'function range': result['function range']
        }
        command(['rm', '-rf', tmp_file])
    json.dump(codegen_input, open(output_file, 'w'), indent=2)


def quixbugs_codegen_output(input_file, output_file, model_dir, model_name, num_output=10):
    tokenizer = AutoTokenizer.from_pretrained(model_dir + model_name + '-multi')
    model = AutoModelForCausalLM.from_pretrained(model_dir + model_name + '-multi')# .to(device_ids[0])
    model.parallelize(device_map)
    
    codegen_output = json.load(open(input_file, 'r'))
    codegen_output['model'] = model_name
    for filename in codegen_output['data']:
        text = codegen_output['data'][filename]['input']

        print('generating', filename)
        
        input_ids = tokenizer(text, return_tensors="pt").input_ids.to(device_ids[0])
        eos_id = tokenizer.convert_tokens_to_ids(tokenizer.eos_token)
        generated_ids = model.generate(
            input_ids, max_new_tokens=128, num_beams=num_output, num_return_sequences=num_output, early_stopping=True,
            pad_token_id=eos_id, eos_token_id=eos_id
        )
        output = []
        for generated_id in generated_ids:
            output.append(tokenizer.decode(generated_id, skip_special_tokens=True))
        codegen_output['data'][filename]['output'] = output
        json.dump(codegen_output, open(output_file, 'w'), indent=2)


def codegen_output_to_patch(output, config):
    if config in ['CODEGEN_COMPLETE_CODEFORM_NOCOMMENT', 'CODEGEN_COMPLETE_CODEFORM_COMMENTFORM_NOCOMMENT']:
        """
        find the } that matches the first { in the output
        """
        output = output.strip().split('\n')
        no_comment_output = [line for line in output if not line.strip().startswith('//')]
        output = '\n'.join(no_comment_output)
        stack = ['{']
        try:
            start_index = output.index('{')
            patch = output[: start_index + 1]
            for c in output[start_index + 1: ]:
                patch += c
                if c == '}':
                    top = stack.pop()
                    if top != '{':
                        return ''
                    if len(stack) == 0:
                        return patch.strip()
                elif c == '{':
                    stack.append(c)
            return ''
        except Exception as e:
            return ''


if __name__ == '__main__':
    model_dir = sys.argv[1]
    for i, config in enumerate(CodeGenInputConfig):
        input_file = CODEGEN_DIR + '../quixbugs/codegen_result/codegen_input_c' + str(i + 1) + '.json'
        
        print("==========Preparing input of QuixBugs benchmark to CODEGEN model, Config: " + config + "==========")
        quixbugs_codegen_input(config, input_file)
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
                                                        
            # model_dir = CODEGEN_DIR + '../models/'
            output_file = CODEGEN_DIR + '../quixbugs/codegen_result/' + '_'.join(model_name.split('-')) + '_output_c' + str(i + 1) + '.json'
            print("==========Generating output of QuixBugs benchmark by " + model_name + ", Config: " + config + "==========")
            quixbugs_codegen_output(input_file, output_file, model_dir, model_name)
            print("==========Output written to " + output_file)
