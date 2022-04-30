import fingerprint.bep.communication

import encryption

FINGERPRINT_PUBLIC_KEY = 111
FINGERPRINT_PRIVATE_KEY = 222

RASPBERRY_PUBLIC_KEY = 888
RASPBERRY_PRIVATE_KEY = 999

class ComSecure(fingerprint.bep.communication.Com):
    def __init__(self, cmd, argument=None, mtu=256):
        super().__init__(cmd, argument, mtu)

    def _tx_application(self, serial):
        print("transmitting")
        valid = send_command()

        # Only execute the command if its signature is valid after being sent across the wire
        if valid:
            return super()._tx_application(serial)
        else:
            return False

    def _rx_application(self, serial):
        print("receiving")
        return super()._rx_application(serial)

    # Simulation of sending a command over an encrypted interface
    def send_command(self):
        # Create a digital signature of the command
        cmd_digital_sig = create_signature(self.cmd)

        # Concatenate the command with its signature, then asymmetrically encrypt this data using the raspberry pi's public key
        data_encrypted = encryption.asymm_encrypt_data(self.cmd + ";" + cmd_digital_sig, RASPBERRY_PUBLIC_KEY)

        # Delete the plaintext version of the command
        self.cmd = None

        # --->
        # THE ENCRYPTED & SIGNED DATA IS SENT "PUBLICALLY"
        # --->

        # Decrypt the command and signature using the raspberry pi's private key
        data_decrypted = encrypt.asymm_decrypt_data(data_encrypted, RASPBERRY_PRIVATE_KEY)

        # Extract both the decrypted command, and the digital signature from the data blob
        cmd = data_decrypted.split(";")[0]
        cmd_digital_sig = data_decrypted.split(";")[1]
        
        # Check the signature
        if check_signature(cmd, cmd_digital_sig):
            # If the signature is valid, set the command as the decrypted command
            self.cmd = cmd
            return True
        else:
            # Otherwise, the command remains 'None' and is not exectued
            return False


    # Simulation of receving a response over an encrypted interface
    def recive_response():
        pass
