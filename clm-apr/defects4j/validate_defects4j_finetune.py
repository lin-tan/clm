import shutil
import json
import sys
import os
import time
import defects4j_command

DEFECTS4J_DIR = os.path.abspath(__file__)[: os.path.abspath(__file__).rindex('/') + 1]
sys.path.append(DEFECTS4J_DIR + '../codegen_finetune/')
sys.path.append(DEFECTS4J_DIR + '../codet5_finetune/')
sys.path.append(DEFECTS4J_DIR + '../plbart_finetune/')
sys.path.append(DEFECTS4J_DIR + '../incoder_finetune/')

from quixbugs_codegen_finetune import codegen_output_to_patch
from quixbugs_codet5_finetune import codet5_output_to_patch
from quixbugs_plbart_finetune import plbart_output_to_patch
from quixbugs_incoder_finetune import incoder_output_to_patch


def insert_fix(filename, start_line, end_line, patch):
    """
    end_row is included in the buggy lines / buggy function
    """
    with open(filename, 'r') as file:
        data = file.readlines()

    with open(filename, 'w') as file:
        for i in range(start_line - 1):
            file.write(data[i])
        file.write(patch.strip() + '\n')
        for i in range(end_line, len(data)):
            file.write(data[i])

def validate_defects4j(input_file, output_file, tmp_dir):
    plausible, total = 0, 0

    if not os.path.exists(tmp_dir):
        defects4j_command.command_with_timeout(['mkdir', tmp_dir])

    model_output = json.load(open(input_file, 'r'))
    validated_result = {'config': model_output['config'], 'data': {}}
    # validated_result = json.load(open(output_file, 'r'))
    for key in model_output['data']:
        if key in validated_result['data']:
            continue
        if 'output' not in model_output['data'][key]:
            continue

        key_list = key.split('_')
        proj, bug_id, loc = key_list[0], key_list[1], key_list[-1]
        path = '_'.join(key_list[2: -1])

        print('start validating', proj, bug_id)
        total += 1
        
        validated_result['data'][key] = {}
        for k, value in model_output['data'][key].items():
            if k != 'output':
                validated_result['data'][key][k] = value
        validated_result['data'][key]['output'] = []
        start_line, end_line = validated_result['data'][key]['loc'].split('-')
        end_line = str(int(end_line) - 1) if end_line != start_line else end_line

        defects4j_command.clean_tmp_folder(tmp_dir)
        defects4j_command.checkout_defects4j_project(proj, bug_id + 'b', tmp_dir)
        if proj == "Mockito":
            print("Mockito needs separate compilation")
            defects4j_command.compile_fix(tmp_dir)

        # check standard test time
        start_time = time.time()
        init_out, init_err = defects4j_command.defects4j_test_suite(tmp_dir)
        standard_time = int(time.time() - start_time)

        # check failed test cases
        failed_test_cases = str(init_out).split(' - ')[1:]
        for i, failed_test_case in enumerate(failed_test_cases):
            failed_test_cases[i] = failed_test_case.strip()
        init_fail_num = len(failed_test_cases)
        print(init_fail_num, str(standard_time) + 's')

        # check triggering failed test cases
        trigger, err = defects4j_command.defects4j_trigger(tmp_dir)
        triggers = trigger.strip().split('\n')
        for i, trigger in enumerate(triggers):
            triggers[i] = trigger.strip()
        print('trigger number:', len(triggers))

        current_is_correct = False
        for rank, patch in enumerate(model_output['data'][key]['output']):
            filename = tmp_dir + path
            shutil.copyfile(filename, filename + '.bak')

            if 'codet5' in input_file:
                patch = codet5_output_to_patch(patch)
                insert_fix(filename, int(start_line), int(end_line), patch)
            elif 'codegen' in input_file:
                patch = codegen_output_to_patch(patch)
                insert_fix(filename, int(start_line), int(end_line), patch)
            elif 'plbart' in input_file:
                patch = plbart_output_to_patch(patch)
                insert_fix(filename, int(start_line), int(end_line), patch)
            elif 'incoder' in input_file:
                patch = incoder_output_to_patch(patch)
                insert_fix(filename, int(start_line), int(end_line), patch)

            if proj == 'Mockito':
                # Mockito needs seperate compile
                defects4j_command.compile_fix(tmp_dir)

            # trigger cases is few and total time is long, we test trigger cases first.
            outs = []
            correctness = None
            start_time = time.time()
            if standard_time >= 10 and len(triggers) <= 5:
                for trigger in triggers:
                    out, err = defects4j_command.defects4j_test_one(tmp_dir, trigger, timeout=min(300, int(2*standard_time)))
                    if 'TIMEOUT' in str(err) or 'TIMEOUT' in str(out):
                        print(plausible, total, rank, 'Time out for patch: ', patch,
                            str(int(time.time() - start_time)) + 's')
                        correctness = 'timeout'
                        break
                    elif 'FAIL' in str(err) or 'FAIL' in str(out):
                        print(plausible, total, rank, 'Uncompilable patch:', patch,
                            str(int(time.time() - start_time)) + 's')
                        correctness = 'uncompilable'
                        break
                    elif "Failing tests: 0" in str(out):
                        continue
                    else:
                        outs += str(out).split(' - ')[1:]
            if len(set(outs)) >= len(triggers):
                # does not pass any one more
                print(plausible, total, rank, 'Wrong patch:', patch,
                    str(int(time.time() - start_time)) + 's')
                correctness = 'wrong'

            if correctness is None:
                # pass at least one more trigger case
                # have to pass all non-trigger
                out, err = defects4j_command.defects4j_test_suite(tmp_dir, timeout=min(300, int(2*standard_time)))

                if 'TIMEOUT' in str(err) or 'TIMEOUT' in str(out):
                    print(plausible, total, rank, 'Time out for patch: ', patch,
                        str(int(time.time() - start_time)) + 's')
                    correctness = 'timeout'
                elif 'FAIL' in str(err) or 'FAIL' in str(out):
                    print(plausible, total, rank, 'Uncompilable patch:', patch,
                        str(int(time.time() - start_time)) + 's')
                    correctness = 'uncompilable'
                elif "Failing tests: 0" in str(out):
                    if not current_is_correct:
                        current_is_correct = True
                        plausible += 1
                    print(plausible, total, rank, 'Plausible patch:', patch,
                        str(int(time.time() - start_time)) + 's')
                    correctness = 'plausible'
                elif len(str(out).split(' - ')[1:]) < init_fail_num:
                    # fail less, could be correct
                    current_failed_test_cases = str(out).split(' - ')[1:]
                    no_new_fail = True
                    for current_failed_test_case in current_failed_test_cases:
                        if current_failed_test_case.strip() not in failed_test_cases:
                            no_new_fail = False
                            break
                    if no_new_fail:
                        # fail less and no new fail cases, could be plausible
                        if not current_is_correct:
                            current_is_correct = True
                            plausible += 1
                        print(plausible, total, rank, 'Plausible patch:', patch,
                                str(int(time.time() - start_time)) + 's')
                        correctness = 'plausible'
                    else:
                        print(plausible, total, rank, 'Wrong patch:', patch,
                                str(int(time.time() - start_time)) + 's')
                        correctness = 'wrong'
                else:
                    print(plausible, total, rank, 'Wrong patch:', patch,
                        str(int(time.time() - start_time)) + 's')
                    correctness = 'wrong'

            validated_result['data'][key]['output'].append({
                'patch': patch, 'correctness': correctness
            })
            shutil.copyfile(filename + '.bak', filename)

        # write after finish validating every bug, to avoid wasting time
        json.dump(validated_result, open(output_file, 'w'), indent=2)

    # write the last time after validating all
    json.dump(validated_result, open(output_file, 'w'), indent=2)


if __name__ == '__main__':
    input_file = sys.argv[1]    # output.json containing the generated patches
    output_file = sys.argv[2]   # validation.json containing the validated result
    tmp_dir = sys.argv[3]       # an empty tmp folder, default ../../tmp_benchmarks/defects4j/
    
    validate_defects4j(input_file, output_file, tmp_dir)
