import subprocess

import encryption

# Enable more detailed logging of command output/errors
DEBUG = True

# Spawns a subprocess for the given shell command, and logs its output
def execute_command(command, human_readable=True):
    process = subprocess.Popen(command, env=encryption.get_tpm_shell_env() ,stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    stdout, stderr = process.communicate()

    log(stdout, human_readable)

    return stdout

# Log a message to the console if debug is enabled
def log(message, human_readable):
    if DEBUG and human_readable:
        print(message.decode("utf-8"))