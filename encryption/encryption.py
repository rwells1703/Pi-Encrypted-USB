import os
import subprocess

import utils
import rfid

def get_tpm_shell_env():
    # Specify the host and port for the TPM server
    env = os.environ.copy()
    env["TPM2TOOLS_TCTI"] = "mssim:host=localhost,port=2321"
    
    return env


def generate_key():
    passcode = rfid.read_card_passcode("key generation")

    print("# STARTED generate AES key")

    stdout = utils.execute_command(["/home/pi/piusb/encryption/generate_key", passcode])
    
    print("# FINISHED generate AES key")

def generate_card_password():
    pass


def decrypt():
    passcode = rfid.read_card_passcode("decryption")

    print("# STARTED decrypting file system")
    stdout = utils.execute_command(["/home/pi/piusb/encryption/decrypt", passcode])
    
    print("# FINISHED decrypting file system")

def encrypt():
    passcode = rfid.read_card_passcode("encryption")

    print("# STARTED encrypting file system")
    stdout = utils.execute_command(["/home/pi/piusb/encryption/encrypt", passcode])
    
    print("# FINISHED encrypting file system")


def start_tpm():
    # Start the TPM server
    tpm_server_proc = subprocess.Popen(["/home/pi/piusb/encryption/stpm/src/tpm_server"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

    try:
        # The 1 second pause also gives the TPM server to start properly
        # TODO: Replace this long pause with checks on the output of the "startup -c" command to see if there is an error
        # iF there is an error, wait and then retry till the server is ready
        stdout, stderr = tpm_server_proc.communicate(timeout=1)
    except subprocess.TimeoutExpired:
        # This should occur if the TPM server started properly
        # as there should be no end-of-file character yet
        pass
    else:
        # There has been an error as the TPM server has already stopped
        print(stdout.decode("utf-8"))

    print("# TPM started")

    return tpm_server_proc

def stop_tpm(tpm_server_proc):
    tpm_server_proc.kill()

def clear_tpm_nv():
    stdout = utils.execute_command(["/home/pi/piusb/encryption/clear_tpm_nv"])

    print("TPM NV RAM has been cleared")

def reset_tpm():
    stdout = utils.execute_command(["/home/pi/piusb/encryption/reset_tpm"])

    print("# TPM has been reset")