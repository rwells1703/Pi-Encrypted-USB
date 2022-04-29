import subprocess

import encryption

# Enable more detailed logging of command output/errors
DEBUG = True

# Spawns a subprocess for the given shell command, and logs its output
def execute_command(command):
    process = subprocess.Popen(command, env=encryption.get_tpm_shell_env() ,stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    stdout, stderr = process.communicate()

    log(stdout.decode("utf-8"))

    return stdout

# Log a message to the console if debug is enabled
def log(message):
    if DEBUG:
        print(message)