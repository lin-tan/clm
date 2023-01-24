import os
import time
import subprocess


def command_with_timeout(cmd, timeout=60):
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

def humaneval_test_suite(algo, humaneval_dir):
    CUR_DIR = os.getcwd()
    FNULL = open(os.devnull, 'w')
    try:
        os.chdir(humaneval_dir)
        out, err = command_with_timeout(["mvn", "test", "-Dtest=TEST_" + algo.upper()], timeout=10)
        os.chdir(CUR_DIR)
        msg = (str(out) + str(err)).upper()
        if "compilation problems".upper() in msg or "compilation failure".upper() in msg:
            return 'uncompilable'
        elif "timeout".upper() in msg:
            return 'timeout'
        elif "build success".upper() in msg:
            return 'plausible'
        else:
            return "wrong"
    except Exception as e:
        print(e)
        os.chdir(CUR_DIR)
        return 'uncompilable'
