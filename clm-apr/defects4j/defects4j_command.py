import os
import subprocess
import shutil
import time


def clean_tmp_folder(tmp_dir):
    if os.path.isdir(tmp_dir):
        for files in os.listdir(tmp_dir):
            file_p = os.path.join(tmp_dir, files)
            try:
                if os.path.isfile(file_p):
                    os.unlink(file_p)
                elif os.path.isdir(file_p):
                    shutil.rmtree(file_p)
            except Exception as e:
                print(e)
    else:
        os.makedirs(tmp_dir)


def checkout_defects4j_project(project, bug_id, tmp_dir):
    FNULL = open(os.devnull, 'w')
    command = "defects4j checkout " + " -p " + project + " -v " + bug_id + " -w " + tmp_dir
    p = subprocess.Popen([command], shell=True, stdout=FNULL, stderr=FNULL)
    p.wait()


def compile_fix(project_dir):
    os.chdir(project_dir)
    p = subprocess.Popen(["defects4j", "compile"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = p.communicate()
    if "FAIL" in str(err) or "FAIL" in str(out):
        return False
    return True


def command_with_timeout(cmd, timeout=300):
    p = subprocess.Popen(cmd, stderr=subprocess.PIPE, stdout=subprocess.PIPE, universal_newlines=True)
    t_beginning = time.time()
    while True:
        if p.poll() is not None:
            break
        seconds_passed = time.time() - t_beginning
        if timeout and seconds_passed > timeout:
            p.terminate()
            return 'TIMEOUT', 'TIMEOUT'
        time.sleep(1)
    out, err = p.communicate()
    return out, err


def defects4j_test_suite(project_dir, timeout=300):
    os.chdir(project_dir)
    out, err = command_with_timeout(["defects4j", "test", "-r"], timeout)
    return out, err


def defects4j_trigger(project_dir, timeout=300):
    os.chdir(project_dir)
    out, err = command_with_timeout(["defects4j", "export", "-p", "tests.trigger"], timeout)
    return out, err


def defects4j_relevant(project_dir, timeout=300):
    os.chdir(project_dir)
    out, err = command_with_timeout(["defects4j", "export", "-p", "tests.relevant"], timeout)
    return out, err


def defects4j_test_one(project_dir, test_case, timeout=300):
    os.chdir(project_dir)
    out, err = command_with_timeout(["defects4j", "test", "-t", test_case], timeout)
    return out, err