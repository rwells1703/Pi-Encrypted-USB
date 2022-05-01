import os
import subprocess
import random
import string

import rfid
import utils

class Encryption:
    # Generates a new random AES key using the TPM
    # then store it within the TPM, sealed against the RFID card passcode
    def generate_key(rfid_passcode):
        print("# STARTED generate AES key")
        stdout = utils.execute_command(["./encryption/scripts/generate_key", rfid_passcode])
        print("# FINISHED generate AES key")

    # Generates a new passcode to be stored on the RFID card
    def generate_card_passcode():
        # The passcode may consist of any letters, numbers and punctuation characters
        alphabet = string.ascii_letters + string.digits + string.punctuation

        # Generate the passcode randomly
        passcode = "".join(random.choice(alphabet) for i in range(16))

        print("# Generated new passcode: " + passcode)
        return passcode

    # Decrypts the file system
    def decrypt(rfid_passcode):
        print("# STARTED decrypting file system")
        stdout = utils.execute_command(["./encryption/scripts/decrypt", rfid_passcode])
        print("# FINISHED decrypting file system")

        if "a policy check failed" in stdout.decode("utf-8"):
            return False
        return True

    # Encrypts the file system and stores it in the ramdisk
    def encrypt(rfid_passcode):
        print("# STARTED encrypting file system")
        stdout = utils.execute_command(["./encryption/scripts/encrypt", rfid_passcode])
        print("# FINISHED encrypting file system")

        if "a policy check failed" in stdout.decode("utf-8"):
            return False
            
        return True


    # Specify the host and port for the TPM server in the shell environment variables
    def get_tpm_shell_env():
        env = os.environ.copy()
        env["TPM2TOOLS_TCTI"] = "mssim:host=localhost,port=2321"
        
        return env


    def asymm_encrypt_data(key_addr, data):
        stdout = utils.execute_command(["./encryption/scripts/asymm_encrypt_data", key_addr, data], human_readable=False)
        print("# Encrypted data with key: " + key_addr)

        return stdout

    def asymm_decrypt_data(key_addr, data):
        stdout = utils.execute_command(["./encryption/scripts/asymm_decrypt_data", key_addr, data], human_readable=False)
        print("# Decrypted data with key: " + key_addr)

        return stdout

    def check_signature(key_addr, data, signature):
        return True

    def create_signature(key_addr, data):
        return "this is a fake signature"