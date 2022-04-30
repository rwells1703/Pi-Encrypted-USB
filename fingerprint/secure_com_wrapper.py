import fingerprint.bep.communication

import encryption

# The persistent memory adresses within the TPM where the keys are stored
FINGERPRINT_KEY_ADDR = "0x81010004"
RASPBERRY_KEY_ADDR = "0x81010005"


class ComSecure(fingerprint.bep.communication.Com):
    def __init__(self, cmd, argument=None, mtu=256):
        super().__init__(cmd, argument, mtu)

    def _tx_application(self, serial):
        print("transmitting")
        valid = self.send_command()
        
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
        cmd_sig = encryption.create_signature(RASPBERRY_KEY_ADDR, self.cmd.decode('utf-8'))

        # Concatenate the command with its signature, then asymmetrically encrypt this data using the raspberry pi's public key
        data_encrypted = encryption.asymm_encrypt_data(RASPBERRY_KEY_ADDR, self.cmd.decode('utf-8') + ";" + cmd_sig)

        # Delete the plaintext version of the command
        self.cmd = None

        # --->
        # THE ENCRYPTED & SIGNED DATA IS SENT "PUBLICLY"
        # --->

        # Decrypt the command and signature using the raspberry pi's private key
        data_decrypted = encryption.asymm_decrypt_data(RASPBERRY_KEY_ADDR, data_encrypted)

        # Extract both the decrypted command, and the digital signature from the data blob
        cmd = data_decrypted.split(";")[0]
        cmd_sig = data_decrypted.split(";")[1]
        
        # Check the signature
        if encryption.check_signature(RASPBERRY_KEY_ADDR, cmd, cmd_sig):
            print(cmd)
            input()
            # Perform lookup of equivalent command here
            command_lookup = None

            # If the signature is valid, set the command as the decrypted command
            self.cmd = command_lookup



            return True
        
        # Otherwise if the signature is invalid,
        # the command remains 'None' and is not exectued
        return False


    # Simulation of receving a response over an encrypted interface
    def receive_response():
        pass
