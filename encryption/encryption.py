import os
import random
import string

import utils

class Encryption:
    # The persistent memory adresses within the TPM where the keys are stored
    RASPBERRY_KEY_ADDR = "0x81010002"
    FINGERPRINT_KEY_ADDR = "0x81010003"

    # Generates a new random AES key using the TPM
    # then store it within the TPM, sealed against the RFID card passcode
    def generate_and_seal_key(rfid_passcode, fingerprint_message, fingerprint_message_signature):
        # Create temporary data and signature files
        Encryption.create_temporary_file("message", fingerprint_message)
        Encryption.create_temporary_file("signature", fingerprint_message_signature)

        print("# STARTED generate and seal AES key")
        stdout = utils.execute_command(["./encryption/scripts/generate_and_seal_key", rfid_passcode, Encryption.FINGERPRINT_KEY_ADDR, Encryption.get_temporary_file_path("message"), Encryption.get_temporary_file_path("signature")])
        print("# FINISHED generate and seal AES key")

        Encryption.delete_temporary_file("message")
        Encryption.delete_temporary_file("signature")

        return True

    # Creates a new AES key and then encrypts the drive with it
    def encrypt_new(rfid_passcode, fingerprint_message, fingerprint_message_signature):
        Encryption.generate_and_seal_key(rfid_passcode, fingerprint_message, fingerprint_message_signature)
        result = Encryption.encrypt(rfid_passcode, fingerprint_message, fingerprint_message_signature)

        return result

    # Generates a new passcode to be stored on the RFID card
    def generate_card_passcode():
        # The passcode may consist of any letters, numbers and punctuation characters
        alphabet = string.ascii_letters + string.digits + string.punctuation

        # Generate the passcode randomly
        passcode = "".join(random.choice(alphabet) for i in range(16))

        print("# Generated new passcode")
        return passcode

    # Unseal the AES key from the TPM
    def unseal_key(rfid_passcode, fingerprint_message, fingerprint_message_signature):
        # Create temporary data and signature files
        Encryption.create_temporary_file("message", fingerprint_message)
        Encryption.create_temporary_file("signature", fingerprint_message_signature)

        print("# STARTED unsealing key")
        stdout = utils.execute_command(["./encryption/scripts/unseal_key", rfid_passcode, Encryption.FINGERPRINT_KEY_ADDR, Encryption.get_temporary_file_path("message"), Encryption.get_temporary_file_path("signature")])
        print("# FINISHED unsealing key")

        if "a policy check failed" in stdout.decode("utf-8"):
            return False
        else:
            aes_key = stdout.split(b"\n")[-2]
            return aes_key

    # Decrypts the file system
    def decrypt(rfid_passcode, fingerprint_message, fingerprint_message_signature):
        aes_key = Encryption.unseal_key(rfid_passcode, fingerprint_message, fingerprint_message_signature)

        if not aes_key:
            return False
        
        print("# STARTED decrypting file system")
        stdout = utils.execute_command(["./encryption/scripts/decrypt", aes_key])
        print("# FINISHED decrypting file system")

        if "bad decrypt" in stdout.decode("utf-8"):
            return False

        return True

    # Encrypts the file system and stores it in the ramdisk
    def encrypt(rfid_passcode, fingerprint_message, fingerprint_message_signature):
        aes_key = Encryption.unseal_key(rfid_passcode, fingerprint_message, fingerprint_message_signature)

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
        stdout = utils.execute_command(["./encryption/scripts/generate_fingerprint_communcation_keys"])
        print("# Generated encryption keys for communication with fingerprint sensor")


    def asymm_encrypt_data(key_addr, data):
        # Create temporary data file
        Encryption.create_temporary_file("data", data)

        stdout = utils.execute_command(["./encryption/scripts/asymm_encrypt_data", key_addr, Encryption.get_temporary_file_path("data")], False)

        # Remove temporary data file
        Encryption.delete_temporary_file("data")

        print("# Encrypted data with key: " + key_addr)

        return stdout


    def asymm_decrypt_data(key_addr, data):
        # Create temporary data file
        Encryption.create_temporary_file("data", data)

        stdout = utils.execute_command(["./encryption/scripts/asymm_decrypt_data", key_addr, Encryption.get_temporary_file_path("data")], False)

        # Remove temporary data file
        Encryption.delete_temporary_file("data")

        print("# Decrypted data with key: " + key_addr)
        
        return stdout

    def create_signature(key_addr, data):
        # Create temporary data file
        Encryption.create_temporary_file("data", data)

        # Create a signature from the data file
        stdout = utils.execute_command(["./encryption/scripts/create_signature", key_addr, Encryption.get_temporary_file_path("data")], False)
        print("# Created signature")

        # Remove temporary data file
        Encryption.delete_temporary_file("data")

        return stdout

    def verify_signature(key_addr, data, signature):
        # Create temporary data and signature files
        Encryption.create_temporary_file("data", data)
        Encryption.create_temporary_file("signature", signature)

        # Verify the data file against the provided signature
        stdout = utils.execute_command(["./encryption/scripts/verify_signature", key_addr, Encryption.get_temporary_file_path("data"), Encryption.get_temporary_file_path("signature")], False)
        print("# Verified signature")

        # Remove temporary data and signature files
        Encryption.delete_temporary_file("data")
        Encryption.delete_temporary_file("signature")

        return stdout

    def encrypt_signature(key_addr, signature):
        part_1 = Encryption.asymm_encrypt_data(key_addr, signature[:len(signature)//2])
        part_2 = Encryption.asymm_encrypt_data(key_addr, signature[len(signature)//2:])

        return part_1 + part_2

    def decrypt_signature(key_addr, encrypted_signature):
        part_1 = Encryption.asymm_decrypt_data(key_addr, encrypted_signature[:len(encrypted_signature)//2])
        part_2 = Encryption.asymm_decrypt_data(key_addr, encrypted_signature[len(encrypted_signature)//2:])

        return part_1 + part_2

    # Get the path of a specific temporary file
    def get_temporary_file_path(name):
        return "./storage/ramdisk/{name}.temp".format(name=name)

    # Writes data to a temporary file so it can be read by the script (as null bytes are not allowed)
    def create_temporary_file(name, data):
        f = open(Encryption.get_temporary_file_path(name), "wb")
        f.write(data)
        f.close()

    # Remove the temporary file
    def delete_temporary_file(name):
        os.remove(Encryption.get_temporary_file_path(name))