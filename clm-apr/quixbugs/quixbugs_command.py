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


def compile_fix(filename, tmp_dir):
    FNULL = open(os.devnull, 'w')
    p = subprocess.call(["javac",
                         tmp_dir + "Node.java",
                         tmp_dir + "WeightedEdge.java",
                         filename], stderr=FNULL)
    return False if p else True


def quixbugs_test_suite(algo, quixbugs_dir):
    QUIXBUGS_MAIN_DIR = quixbugs_dir
    CUR_DIR = os.getcwd()
    FNULL = open(os.devnull, 'w')
    JAR_DIR = ''
    try:
        os.chdir(QUIXBUGS_MAIN_DIR)
        p1 = subprocess.Popen(["javac", "-cp", ".:java_programs:" + JAR_DIR + "junit4-4.12.jar:" + JAR_DIR +
                               "hamcrest-all-1.3.jar", "java_testcases/junit/" + algo.upper() + "_TEST.java"],
                              stdout=subprocess.PIPE, stderr=FNULL, universal_newlines=True)
        out, err = command_with_timeout(
            ["java", "-cp", ".:java_programs:" + JAR_DIR + "junit4-4.12.jar:" + JAR_DIR + "hamcrest-all-1.3.jar",
             "org.junit.runner.JUnitCore", "java_testcases.junit." + algo.upper() + "_TEST"], timeout=5
        )

        os.chdir(CUR_DIR)
        if "FAILURES" in str(out) or "FAILURES" in str(err):
            return 'wrong'
        elif "TIMEOUT" in str(out) or "TIMEOUT" in str(err):
            return 'timeout'
        else:
            return 'plausible'
    except Exception as e:
        print(e)
        os.chdir(CUR_DIR)
        return 'uncompilable'


