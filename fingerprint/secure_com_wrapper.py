import os

import fingerprint.bep.communication

import encryption

class ComSecure(fingerprint.bep.communication.Com):
    def __init__(self, cmd, argument=None, mtu=256):
        super().__init__(cmd, argument, mtu)

        # Stores a signature for the last transmitted command/received response
        self.last_communication_signature = None

    # Wraps communication (commands) from PI -> FINGERPRINT
    def _tx_transport(self, serial, seq_nr, seq_len, app_data):
        app_data = self.securely_communicate(app_data, encryption.Encryption.RASPBERRY_KEY_ADDR, encryption.Encryption.FINGERPRINT_KEY_ADDR)

        return super()._tx_transport(serial, seq_nr, seq_len, app_data)  

    # Wraps communication (responses) from FINGERPRINT -> PI
    def _rx_transport(self, serial):
        status, application_package = super()._rx_transport(serial)

        application_package = self.securely_communicate(application_package, encryption.Encryption.FINGERPRINT_KEY_ADDR, encryption.Encryption.RASPBERRY_KEY_ADDR)

        return status, application_package

    # Simulation of sending data over an encrypted connection
    def securely_communicate(self, data, senders_key_address, receivers_key_address):
        # Create a digital signature of the data using the SENDER'S PRIVATE KEY
        data_sig = encryption.Encryption.create_signature(senders_key_address, data)

        # Write the app data to a temporary file so it can be read by the encryption script
        # (It cannot be input as a command line argument as it may contain null bytes)
        f = open("./storage/ramdisk/data.dat", "wb")
        combined_data = data + (";" + data_sig).encode("utf-8")
        f.write(combined_data)
        f.close()

        # Concatenate the data with its signature, then asymmetrically encrypt this data using the RECEIVER'S PUBLIC KEY
        data_encrypted = encryption.Encryption.asymm_encrypt_data(receivers_key_address, "./storage/ramdisk/data.dat")

        # Remove the app data file
        os.remove("./storage/ramdisk/data.dat")

        # Delete the plaintext versions of the data and signature
        data = None
        data_sig = None

        # --->
        # THE ENCRYPTED & SIGNED DATA IS SENT "PUBLICLY"
        # --->

        # Again write the (now encrypted) app data to a temporary file for reading
        f = open("./storage/ramdisk/data_encrypted.dat", "wb")
        f.write(data_encrypted)
        f.close()

        # Decrypt the command and signature using the RECEIVER'S PRIVATE KEY
        data_decrypted = encryption.Encryption.asymm_decrypt_data(receivers_key_address, "./storage/ramdisk/data_encrypted.dat")

        # Remove the encrypted app data file
        os.remove("./storage/ramdisk/data_encrypted.dat")
        
        # Extract both the decrypted command, and the digital signature from the data blob
        data = data_decrypted.split(b';')[0]
        data_sig = data_decrypted.split(b';')[1]

        # Save this signature in the class, incase it needs to be used for a TPM policy authorization
        self.last_communication_signature = data_sig

        # Check the signature against the SENDER'S PUBLIC KEY
        if encryption.Encryption.check_signature(senders_key_address, data, data_sig):
            return data
        
        # Otherwise if the signature is invalid,
        # the command remains 'None' and is not exectued
        return False