import os
import random
import string

import rfid
import utils

class Encryption:
    # The persistent memory adresses within the TPM where the keys are stored
    RASPBERRY_KEY_ADDR = "0x81010002"
    FINGERPRINT_KEY_ADDR = "0x81010003"

    # Generates a new random AES key using the TPM
    # then store it within the TPM, sealed against the RFID card passcode
    def generate_and_seal_key(rfid_passcode, fingerprint_signature):
        print("# STARTED generate AES key")
        stdout = utils.execute_command(["./encryption/scripts/generate_and_seal_key", rfid_passcode, fingerprint_signature])
        print("# FINISHED generate AES key")

    # Generates a new passcode to be stored on the RFID card
    def generate_card_passcode():
        # The passcode may consist of any letters, numbers and punctuation characters
        alphabet = string.ascii_letters + string.digits + string.punctuation

        # Generate the passcode randomly
        passcode = "".join(random.choice(alphabet) for i in range(16))

        print("# Generated new passcode: " + passcode)
        return passcode

    # Unseal the AES key from the TPM
    def unseal_key(rfid_passcode, fingerprint_signature):
        print("# STARTED unsealing key")
        stdout = utils.execute_command(["./encryption/scripts/unseal_key", rfid_passcode, fingerprint_signature])
        print("# FINISHED unsealing key")

        if "a policy check failed" in stdout.decode("utf-8"):
            return False
        else:
            aes_key = stdout.split(b"\n")[-2]
            return aes_key

    # Decrypts the file system
    def decrypt(rfid_passcode, fingerprint_signature):
        aes_key = Encryption.unseal_key(rfid_passcode, fingerprint_signature)

        if not aes_key:
            return False
        
        print("# STARTED decrypting file system")
        stdout = utils.execute_command(["./encryption/scripts/decrypt", aes_key])
        print("# FINISHED decrypting file system")

        if "bad decrypt" in stdout.decode("utf-8"):
            return False

        return True
            

    # Encrypts the file system and stores it in the ramdisk
    def encrypt(rfid_passcode, fingerprint_signature):
        aes_key = Encryption.unseal_key(rfid_passcode, fingerprint_signature)

        if not aes_key:
            return False

        print("# STARTED encrypting file system")
        stdout = utils.execute_command(["./encryption/scripts/encrypt", aes_key])
        print("# FINISHED encrypting file system")

        if "bad decrypt" in stdout.decode("utf-8"):
            return False
        
        return True

    # Specify the host and port for the TPM server in the shell environment variables
    def get_tpm_shell_env():
        env = os.environ.copy()
        env["TPM2TOOLS_TCTI"] = "mssim:host=localhost,port=2321"
        
        return env


    def generate_fingerprint_communication_keys():
        stdout = utils.execute_command(["./encryption/scripts/generate_fingerprint_communcation_keys"], False)
        print("# Generated encryption keys for communication with fingerprint sensor")

    def asymm_encrypt_data(key_addr, data):
        stdout = utils.execute_command(["./encryption/scripts/asymm_encrypt_data", key_addr, data], False)
        print("# Encrypted data with key: " + key_addr)

        return stdout

    def asymm_decrypt_data(key_addr, data):
        stdout = utils.execute_command(["./encryption/scripts/asymm_decrypt_data", key_addr, data], False)
        print("# Decrypted data with key: " + key_addr)

        return stdout

    def check_signature(key_addr, data, signature):
        return True

    def create_signature(key_addr, data):
        return "this is a fake signature"