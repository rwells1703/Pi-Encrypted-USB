import os
import subprocess

import rfid
import utils

# Generates a new random AES key using the TPM
# then store it within the TPM, sealed against the RFID card passcode
def generate_key():
    passcode = rfid.read_card_passcode("key generation")

    print("# STARTED generate AES key")
    stdout = utils.execute_command(["./encryption/scripts/generate_key", passcode])
    print("# FINISHED generate AES key")

# Generates a new passcode to be stored on the RFID card
def generate_card_passcode():
    pass


# Decrypts the file system
def decrypt():
    passcode = rfid.read_card_passcode("decryption")

    print("# STARTED decrypting file system")
    stdout = utils.execute_command(["./encryption/scripts/decrypt", passcode])
    print("# FINISHED decrypting file system")

# Encrypts the file system and stores it in the ramdisk
def encrypt():
    passcode = rfid.read_card_passcode("encryption")

    print("# STARTED encrypting file system")
    stdout = utils.execute_command(["./encryption/scripts/encrypt", passcode])
    print("# FINISHED encrypting file system")


# Specify the host and port for the TPM server in the shell environment variables
def get_tpm_shell_env():
    env = os.environ.copy()
    env["TPM2TOOLS_TCTI"] = "mssim:host=localhost,port=2321"
    
    return env

# Start the TPM server
def start_tpm():
    # Spawn the server subprocess
    tpm_server_proc = subprocess.Popen(["./encryption/stpm/src/tpm_server"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

    try:
        # The 1 second pause also gives the TPM server to start properly
        # TODO: Replace this long pause with checks on the output of the "startup -c" command to see if there is an error
        # if there is an error, wait and then retry till the server is ready
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

# Stop the TPM server
def stop_tpm(tpm_server_proc):
    tpm_server_proc.kill()
    print("# TPM stopped")

# Reset the TPM to a blank state (clears NVRAM and changes owner hierarchy password)
def reset_tpm():
    stdout = utils.execute_command(["./encryption/scripts/reset_tpm"])
    print("# TPM has been reset")