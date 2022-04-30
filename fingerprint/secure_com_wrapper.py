import os

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
        return super()._tx_application(serial)

    def _rx_application(self, serial):
        print("receiving")
        return super()._rx_application(serial)

    def _tx_transport(self, serial, seq_nr, seq_len, app_data):
        app_data = self.send_app_data(app_data)

        return super()._tx_transport(serial, seq_nr, seq_len, app_data)  

    # Simulation of sending app_data for a command over an encrypted connection
    def send_app_data(self, app_data):
        # Create a digital signature of the command
        app_data_sig = encryption.create_signature(RASPBERRY_KEY_ADDR, app_data)

        # Write the app data to a temporary file so it can be read by the encryption script
        # (It cannot be input as a command line argument as it may contain null bytes)
        f = open("storage/ramdisk/app_data.dat", "wb")
        combined_data = app_data + (";" + app_data_sig).encode("utf-8")
        f.write(combined_data)
        f.close()

        # Concatenate the data with its signature, then asymmetrically encrypt this data using the raspberry pi's public key
        app_data_encrypted = encryption.asymm_encrypt_data(RASPBERRY_KEY_ADDR, "storage/ramdisk/app_data.dat")

        # Remove the app data file
        os.remove("storage/ramdisk/app_data.dat")

        # Delete the plaintext version of the data
        app_data = None

        # --->
        # THE ENCRYPTED & SIGNED DATA IS SENT "PUBLICLY"
        # --->

        # Again write the (now encrypted) app data to a temporary file for reading
        f = open("storage/ramdisk/app_data_encrypted.dat", "wb")
        f.write(app_data_encrypted)
        f.close()

        # Decrypt the command and signature using the raspberry pi's private key
        app_data_decrypted = encryption.asymm_decrypt_data(RASPBERRY_KEY_ADDR, "storage/ramdisk/app_data_encrypted.dat")

        # Remove the encrypted app data file
        os.remove("storage/ramdisk/app_data_encrypted.dat")

        # Extract both the decrypted command, and the digital signature from the data blob
        app_data = app_data_decrypted.split(b';')[0]
        app_data_sig = app_data_decrypted.split(b';')[1]

        # Check the signature
        if encryption.check_signature(RASPBERRY_KEY_ADDR, app_data, app_data_sig):
            return app_data
        
        # Otherwise if the signature is invalid,
        # the command remains 'None' and is not exectued
        return False


    # Simulation of receving a response over an encrypted interface
    def receive_response():
        pass
