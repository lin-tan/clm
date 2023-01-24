import re
import sys
import os
import json
import codecs
import subprocess
import time
from plbart_config import PLBartInputConfig
from transformers import PLBartForConditionalGeneration, PLBartTokenizer

PLBART_DIR = os.path.abspath(__file__)[: os.path.abspath(__file__).rindex('/') + 1]
JAVA_DIR = PLBART_DIR + '../../jasper/'

def command(cmd):
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output, err = process.communicate()
    if output != b'' or err != b'':
        print(output)
        print(err)
    return output, err

def get_plbart_input(filename, start, end, config, tmp_file):
    os.chdir(JAVA_DIR)
    command([
        'java', '-cp', '.:target:lib/*', 'clm.plbart.PLBartInputParser',
        filename, start, end, config, tmp_file
    ])

def humaneval_plbart_input(config, output_file, humaneval_dir):
    loc_fp = codecs.open(PLBART_DIR + '../humaneval/humaneval_loc.txt', 'r', 'utf-8')
    plbart_input = {'config': config, 'data': {}}
    for line in loc_fp.readlines():
        filename, rem_loc = line.strip().split()
        start, end = rem_loc.split('-')
        end = str(int(end) - 1) if end != start else end
        tmp_file = PLBART_DIR + '../humaneval/tmp.json'
        get_plbart_input(humaneval_dir + 'src/main/java/humaneval/buggy/' + filename + '.java', start, end, config, tmp_file)
        
        if not os.path.exists(tmp_file):
            print(filename, 'failed.', tmp_file, 'not found.')
        print(filename, 'succeeded')

        result = json.load(open(tmp_file, 'r'))
        if config == 'PLBART_SEQFORM_MASKFORM_NOCOMMENT':
            plbart_input['data'][filename] = {
                'loc': rem_loc,
                'input': '<s> ' + re.sub('\\s+', ' ', result['input']).strip() + ' </s> java',
                'function range': result['function range']
            }
        elif config == 'PLBART_SEQFORM_COMMENTFORM_NOCOMMENT':
            result['input'] = re.sub('/\\* buggy line:', '/* ', result['input'])
            plbart_input['data'][filename] = {
                'loc': rem_loc,
                'input': '<s> ' + re.sub('\\s+', ' ', result['input']).strip() + ' </s> java',
                'function range': result['function range']
            }
        command(['rm', '-rf', tmp_file])
    json.dump(plbart_input, open(output_file, 'w'), indent=2)

def humaneval_plbart_output(input_file, output_file, model_dir, model_name, num_output=10):
    plbart_output = json.load(open(input_file, 'r'))
    if plbart_output['config'] in ['PLBART_SEQFORM_MASKFORM_NOCOMMENT', 'PLBART_SEQFORM_COMMENTFORM_NOCOMMENT']:
        plbart_output['model'] = model_name
        tokenizer = PLBartTokenizer.from_pretrained(model_dir + model_name, src_lang="java", tgt_lang="java")
        model = PLBartForConditionalGeneration.from_pretrained(model_dir + model_name).to(device_id)
    else:
        assert False, 'unrecognized config'
    start_time = time.time()
    for filename in plbart_output['data']:
        text = plbart_output['data'][filename]['input']

        print('generating', filename)

        input_ids = tokenizer(text, add_special_tokens=False, return_tensors="pt").input_ids.to(device_id)
        generated_ids = model.generate(
            input_ids, max_length=512, num_beams=num_output, num_return_sequences=num_output, 
            early_stopping=True, decoder_start_token_id=tokenizer.lang_code_to_id["java"]
        )
        output = []
        for generated_id in generated_ids:
            output.append(tokenizer.decode(generated_id, skip_special_tokens=True))
        plbart_output['data'][filename]['output'] = output
        json.dump(plbart_output, open(output_file, 'w'), indent=2)
    total_time = int(time.time() - start_time)
    plbart_output['time'] = total_time
    json.dump(plbart_output, open(output_file, 'w'), indent=2)


if __name__ == '__main__':
    device_id = 0   # need one GPU with 12GB memory (CPU is also ok)
    model_dir = sys.argv[1]
    humaneval_dir = PLBART_DIR + '../../humaneval-java/'
    for i, config in enumerate(PLBartInputConfig):
        input_file = PLBART_DIR + '../humaneval/plbart_result/plbart_input_c' + str(i + 1) + '.json'
        
        print("==========Preparing input of HumanEval benchmark to PLBART model, Config: " + config + "==========")
        humaneval_plbart_input(config, input_file, humaneval_dir=humaneval_dir)
        print("==========Input written to " + input_file)
        
        for model_name in ('plbart-base', 'plbart-large'):
            output_file = PLBART_DIR + '../humaneval/plbart_result/' + '_'.join(model_name.split('-')) + '_output_c' + str(i + 1) + '.json'
            # model_dir = PLBART_DIR + '../models/'
            print("==========Generating output of HumanEval benchmark by " + model_name + ", Config: " + config + "==========")
            humaneval_plbart_output(input_file, output_file, model_dir, model_name)
            print("==========Output written to " + output_file)
