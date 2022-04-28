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