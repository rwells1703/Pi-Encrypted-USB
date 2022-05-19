import fingerprint.bep.communication

import config
import encryption

class ComSecure(fingerprint.bep.communication.Com):
    def __init__(self, cmd, argument=None, mtu=256):
        super().__init__(cmd, argument, mtu)

        # Stores the last transmitted/received message and its signature
        self.last_message = None
        self.last_message_signature = None

    # Wraps communication (commands) from PI -> FINGERPRINT
    def _tx_transport(self, serial, seq_nr, seq_len, app_data):
        app_data = self.securely_communicate(app_data, encryption.Encryption.RASPBERRY_KEY_ADDR, encryption.Encryption.FINGERPRINT_KEY_ADDR)

        return super()._tx_transport(serial, seq_nr, seq_len, app_data)  

    # Wraps communication (responses) from FINGERPRINT -> PI
    def _rx_transport(self, serial):
        status, application_package = super()._rx_transport(serial)

        application_package = self.securely_communicate(application_package, encryption.Encryption.FINGERPRINT_KEY_ADDR, encryption.Encryption.RASPBERRY_KEY_ADDR)

        if application_package == None:
            status = False
            
        return status, application_package

    # Simulation of sending data over an encrypted connection
    def securely_communicate(self, data, senders_key_address, receivers_key_address):
        # Create a digital signature of the data using the SENDER'S PRIVATE KEY
        data_sig = encryption.Encryption.create_signature(senders_key_address, data)

        # Only encrypt communications if configuration flag is set
        if config.SECURE_FINGERPRINT_COMMS:
            encryption.Encryption.create_temporary_file("data", data)
            encryption.Encryption.create_temporary_file("signature", data_sig)

            # Asymmetrically encrypt the data and signature using the RECEIVER'S PUBLIC KEY
            data_encrypted = encryption.Encryption.asymm_encrypt_data(receivers_key_address, data)
            data_sig_encrypted = encryption.Encryption.encrypt_signature(receivers_key_address, data_sig)

            # Delete the plaintext versions of the data and signature
            data = None
            data_sig = None

            # --->
            # THE ENCRYPTED & SIGNED DATA IS SENT "PUBLICLY"
            # --->

            # Decrypt the command and signature using the RECEIVER'S PRIVATE KEY
            data = encryption.Encryption.asymm_decrypt_data(receivers_key_address, data_encrypted)
            data_sig = encryption.Encryption.decrypt_signature(receivers_key_address, data_sig_encrypted)

            # Check the signature against the SENDER'S PUBLIC KEY
            stdout = encryption.Encryption.verify_signature(senders_key_address, data, data_sig)

            # If the signature is invalid do not run the command
            if b"Verify signature failed" in stdout:
                print("damn....")
                return None

        # Save this message and its signature in the class, incase it needs to be used for a TPM policy authorization
        self.last_message = data
        self.last_message_signature = data_sig
        
        return data