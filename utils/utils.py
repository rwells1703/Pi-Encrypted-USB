import subprocess

import encryption

debug = False

def execute_command(command):
    process = subprocess.Popen(command, env=encryption.get_tpm_shell_env() ,stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    stdout, stderr = process.communicate()

    if debug:
        print(stdout.decode("utf-8"))

    return stdout