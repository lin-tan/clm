import os
import sys
import json
import codecs
import subprocess
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


def quixbugs_codet5_input(config, output_file):
    loc_fp = codecs.open(CODET5_DIR + '../quixbugs/quixbugs_loc.txt', 'r', 'utf-8')
    codet5_input = {'config': config, 'data': {}}
    # codet5_input = json.load(open(output_file, 'r'))
    for line in loc_fp.readlines():
        filename, rem_loc, add_loc = line.strip().split()
        start, end = rem_loc.split('-')
        end = str(int(end) - 1) if end != start else end
        tmp_file = CODET5_DIR + '../quixbugs/tmp.json'
        get_codet5_input(CODET5_DIR + '../quixbugs/java_programs/' + filename + '.java', start, end, config, tmp_file)
        
        if not os.path.exists(tmp_file):
            print(filename, 'failed.', output_file, 'not found.')
        print(filename, 'succeeded')

        result = json.load(open(tmp_file, 'r'))
        codet5_input['data'][filename] = {
            'loc': rem_loc,
            'input': result['input'],
            'function range': result['function range']
        }
        command(['rm', '-rf', tmp_file])
    json.dump(codet5_input, open(output_file, 'w'), indent=2)


def quixbugs_codet5_output(input_file, output_file, model_dir, model_name, num_output=10):
    codet5_output = json.load(open(input_file, 'r'))
    if codet5_output['config'] in ['CODET5_BASE_CODEFORM_MASKFORM_NOCOMMENT', 'CODET5_BASE_CODEFORM_COMMENTFORM_NOCOMMENT']:
        codet5_output['model'] = model_name
        tokenizer = RobertaTokenizer.from_pretrained(model_dir + model_name)
        model = T5ForConditionalGeneration.from_pretrained(model_dir + model_name).to(device_id)
    # elif codet5_output['config'] == 'CODET5_REFINE_CODEFORM_NOCOMMENT':
    #     codet5_output['model'] = model_name
    #     tokenizer = RobertaTokenizer.from_pretrained(model_dir + model_name)
    #     model = T5ForConditionalGeneration.from_pretrained(model_dir + model_name)
    else:
        assert False, 'unrecognized config'
    for filename in codet5_output['data']:
        text = codet5_output['data'][filename]['input']

        print('generating', filename)

        input_ids = tokenizer(text, return_tensors="pt").input_ids.to(device_id)
        generated_ids = model.generate(input_ids, max_length=512, num_beams=num_output, num_return_sequences=num_output)
        output = []
        for generated_id in generated_ids:
            output.append(tokenizer.decode(generated_id, skip_special_tokens=True))
        codet5_output['data'][filename]['output'] = output
    json.dump(codet5_output, open(output_file, 'w'), indent=2)


def codet5_output_to_patch(output, config):
    if config in ['CODET5_BASE_CODEFORM_MASKFORM_NOCOMMENT', 'CODET5_BASE_CODEFORM_COMMENTFORM_NOCOMMENT']:
        return output.strip()
    elif config == 'CODET5_REFINE_CODEFORM_NOCOMMENT':
        stack = ['{']
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


if __name__ == '__main__':
    device_id = 0   # need one GPU with 12GB memory (CPU is also ok)
    model_dir = sys.argv[1]
    for i, config in enumerate(CodeT5InputConfig):
        if config == 'CODET5_REFINE_CODEFORM_NOCOMMENT':
            continue
        
        input_file = CODET5_DIR + '../quixbugs/codet5_result/codet5_input_c' + str(i + 1) + '.json'
        print("==========Preparing input of QuixBugs benchmark to CODET5 model, Config: " + config + "==========")
        quixbugs_codet5_input(config, input_file)
        print("==========Input written to " + input_file)
        
        for model_name in ('codet5-small', 'codet5-base', 'codet5-large'):
            output_file = CODET5_DIR + '../quixbugs/codet5_result/' + '_'.join(model_name.split('-')) + '_output_c' + str(i + 1) + '.json'
            # model_dir = CODET5_DIR + '../models/'
            print("==========Generating output of QuixBugs benchmark by " + model_name + ", Config: " + config + "==========")
            quixbugs_codet5_output(input_file, output_file, model_dir, model_name)
            print("==========Output written to " + output_file)
