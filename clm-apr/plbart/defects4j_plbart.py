import codecs
import json
import sys
import os
import re
import subprocess
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

def defects4j_plbart_input(config, output_file, tmp_dir):
    loc_fp = codecs.open(PLBART_DIR + '../defects4j/defects4j_loc.txt', 'r', 'utf-8')
    plbart_input = {'config': config, 'data': {}}
    for line in loc_fp.readlines():
        proj, bug_id, path, rem_loc, add_loc = line.strip().split()
        start, end = rem_loc.split('-')
        end = str(int(end) - 1) if end != start else end
        tmp_file = PLBART_DIR + '../defects4j/tmp.json'

        subprocess.run(['defects4j', 'checkout', '-p', proj, '-v', bug_id + 'b', '-w', tmp_dir], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        get_plbart_input(tmp_dir + path, start, end, config, tmp_file)
        
        if not os.path.exists(tmp_file):
            print(proj, bug_id, 'failed.', tmp_file, 'not found.')
            continue
        print(proj, bug_id, 'succeeded')

        result = json.load(open(tmp_file, 'r'))
        if result['input'].strip() == '':
            print(proj, bug_id, 'failed. all empty.')
            continue
        result = json.load(open(tmp_file, 'r'))
        
        if config == 'PLBART_SEQFORM_MASKFORM_NOCOMMENT':
            plbart_input['data'][proj + '_' + bug_id + '_' + path + '_' + rem_loc] = {
                'loc': rem_loc,
                'input': '<s> ' + re.sub('\\s+', ' ', result['input']).strip() + ' </s> java',
                'function range': result['function range']
            }
        elif config == 'PLBART_SEQFORM_COMMENTFORM_NOCOMMENT':
            result['input'] = re.sub('/\\* buggy line:', '/* ', result['input'])
            plbart_input['data'][proj + '_' + bug_id + '_' + path + '_' + rem_loc] = {
                'loc': rem_loc,
                'input': '<s> ' + re.sub('\\s+', ' ', result['input']).strip() + ' </s> java',
                'function range': result['function range']
            }

        command(['rm', '-rf', tmp_file])
        command(['rm', '-rf', tmp_dir])
        json.dump(plbart_input, open(output_file, 'w'), indent=2)

def defects4j_plbart_output(input_file, output_file, model_dir, model_name, num_output=10):
    tokenizer = PLBartTokenizer.from_pretrained(model_dir + model_name, src_lang="java", tgt_lang="java")
    model = PLBartForConditionalGeneration.from_pretrained(model_dir + model_name).to(device_id)
    
    plbart_output = json.load(open(input_file, 'r'))
    plbart_output['model'] = model_name
    for filename in plbart_output['data']:
        text = plbart_output['data'][filename]['input']

        print('generating', filename)

        try:
            input_ids = tokenizer(text, add_special_tokens=False, return_tensors="pt").input_ids.to(device_id)
            if input_ids.size(1) >= 512:
                print('input too long:', input_ids.size(1), 'skip')
                continue
            generated_ids = model.generate(
                input_ids, max_length=512, num_beams=num_output, num_return_sequences=num_output, 
                early_stopping=True, decoder_start_token_id=tokenizer.lang_code_to_id["java"]
            )
            output = []
            for generated_id in generated_ids:
                output.append(tokenizer.decode(generated_id, skip_special_tokens=True))
        except Exception as e:
            output = []
            
        plbart_output['data'][filename]['output'] = output
        json.dump(plbart_output, open(output_file, 'w'), indent=2)


if __name__ == '__main__':
    device_id = 0   # need one GPU with 12GB memory
    model_dir = sys.argv[1]
    for i, config in enumerate(PLBartInputConfig):
        input_file = PLBART_DIR + '../defects4j/plbart_result/plbart_input_c' + str(i + 1) + '.json'
        
        print("==========Preparing input of Defects4J benchmark to PLBART model, Config: " + config + "==========")
        defects4j_plbart_input(config, input_file, tmp_dir='/tmp/plbart/')
        print("==========Input written to " + input_file)
        
        for model_name in ('plbart-base', 'plbart-large'):
            output_file = PLBART_DIR + '../defects4j/plbart_result/' + '_'.join(model_name.split('-')) + '_output_c' + str(i + 1) + '.json'
            # model_dir = PLBART_DIR + '../../models/'
            print("==========Generating output of Defects4J benchmark by " + model_name + ", Config: " + config + "==========")
            defects4j_plbart_output(input_file, output_file, model_dir, model_name)
            print("==========Output written to " + output_file)
