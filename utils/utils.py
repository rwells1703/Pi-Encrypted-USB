import subprocess

import encryption

# Enable more detailed logging of command output/errors
DEBUG = False

# Spawns a subprocess for the given shell command, and logs its output
def execute_command(command, show_log=True):
    process = subprocess.Popen(command, env=encryption.get_tpm_shell_env() ,stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    stdout, stderr = process.communicate()

    log(stdout, show_log)

    return stdout

# Log a message to the console if debug is enabled
def log(message, show_log=True):
    if DEBUG and show_log:
        print(message.decode("utf-8"))