#!/usr/bin/env python3

import time
import os
import signal

import rfid
import utils
import encryption
import storage
import fingerprint
import display
import config

class Main:
    def __init__(self):
        self.main_menu = {
            "Mount": self.mount,
            "Eject": self.eject,
            "Reset": self.reset,
            "Poweroff": self.poweroff
        }

        self.mounted = False
        self.rfid_passcode = None

    def start(self):
        os.chdir("/home/pi/piusb")

        storage.remove_usb_gadget(False)
        storage.delete_fs_image(False)
        storage.unmount_tmpfs(False)
        
        # Runs the "stop" function when the program closes (e.g. if user presses ctrl+c)
        signal.signal(signal.SIGINT, self.close)

        self.tpm = encryption.TPM()
        self.tpm.restart()
        
        self.fingerprint = fingerprint.Fingerprint()

        storage.create_usb_gadget_help()

        if config.GUI:
            self.display = display.Display()
            self.display.draw_menu(self.main_menu, "Main Menu")
        else:
            print("# GUI Disabled")

    # Safely stop running processes and clean up temporary data
    def stop(self):
        storage.remove_usb_gadget(False)
        storage.delete_fs_image(False)
        storage.unmount_tmpfs(False)

        if config.GUI:
            self.display.stop()

        self.tpm.stop()

    # Mount the storage drive, so it appears on the host computer
    def mount(self):
        if self.mounted:
            self.display.draw_message("Already mounted!")
            print("# Already mounted!")
            time.sleep(1)
        else:
            self.display.draw_message("Mounting...")

            storage.mount_tmpfs()

            valid = False
            tries = 3

            while not valid:
                if tries == 0:
                    self.poweroff()

                # Get the passcode from the RFID card
                self.display.draw_message("Tap card")
                self.rfid_passcode = rfid.read_card_passcode("decryption")
                self.display.draw_message("Card found")

                # Get signed identification from the fingerprint sensor
                self.display.draw_message("Scan fingerprint")
                fingerprint_match, fingerprint_id, fingerprint_message, fingerprint_message_signature = self.fingerprint.identify()
                self.display.draw_message("Fingerprint scanned")
                time.sleep(1)
                self.display.draw_message("Decrypting...")

                # If the fingerprint was valid, move onto the next stage of authentication
                if fingerprint_match:
                    print("# Matched fingerprint")

                    valid = encryption.Encryption.decrypt(self.rfid_passcode, fingerprint_message, fingerprint_message_signature)

                    if valid:
                        print("# Correct")
                        self.display.draw_message("Correct")
                        time.sleep(2)
                        break

                # Otherwise, the authorisation was invalid  
                tries -= 1

                # Provide a warning message
                self.display.draw_message("Incorrect\n{tries} tries left\nShutting down".format(tries=tries))
                time.sleep(2)


            # If the user has run out of tries to enter
            if tries == 0:
                self.display.draw_message("Out of tries")
                time.sleep(2)
                self.poweroff()

            if config.AUTH_CARD_ON_EJECT:
                self.rfid_passcode = None

            # Delete any old USB gadget files that may be left over (e.g. the help drive or a fs left from a program crash)
            # logs are now shown because it will display error messages, during normal functionality
            # (ie. it will attempt to delete files that already exist)
            storage.remove_usb_gadget(False)

            # The new USB gadget files and then created
            storage.create_usb_gadget()

            self.mounted = True

            self.display.draw_message("Drive mounted!")
            print("# Drive mounted!")
            time.sleep(1)

    # Eject the storage drive from the host computer
    def eject(self):
        if not self.mounted:
            self.display.draw_message("Not mounted!")
            print("# Not mounted!")
        else:
            self.display.draw_message("Ejecting...")

            # Extra check for the extra security option
            if config.AUTH_CARD_ON_EJECT:
                self.display.draw_message("Tap card")
                self.rfid_passcode = rfid.read_card_passcode("encryption")
                self.display.draw_message("Card found") 

            # Get signed identification from the fingerprint sensor
            self.display.draw_message("Scan fingerprint")
            fingerprint_match, fingerprint_id, fingerprint_message, fingerprint_message_signature = self.fingerprint.identify()
            self.display.draw_message("Fingerprint scanned")

            storage.remove_usb_gadget()

            # Encrypt the drive
            encryption.Encryption.encrypt(self.rfid_passcode, fingerprint_message, fingerprint_message_signature)
            
            if config.AUTH_CARD_ON_EJECT:
                self.rfid_passcode = None

            storage.unmount_tmpfs()

            self.mounted = False

            self.display.draw_message("Drive ejected!")
            print("# Drive ejected!")
        time.sleep(1)

    # Power off the device safely
    def poweroff(self):
        self.stop()
        utils.execute_command(["poweroff"])

    # Close the application in response to a force exit (e.g. ctrl+c)
    def close(self, sig=None, frame=None):
        self.stop()
        exit()

    # Reset the device to a new blank state
    def reset(self):       
        self.display.draw_message("Resetting..")

        # Remove any existing USB drives before resetting (this forces the host to eject)
        storage.remove_usb_gadget()
        
        self.mounted = False
        
        # Reset the TPM to blank
        self.tpm.reset()

        # Generate encrytion keys for communicating with fingerprint sensor
        encryption.Encryption.generate_fingerprint_communication_keys()

        # Create a new file system image
        storage.create_fs_image()

        # Prompt the user to tap the RFID card
        self.display.draw_message("Tap card")
        # Generate a new passcode and write it to the RFID card
        rfid_passcode = rfid.reset_card_passcode()
        self.display.draw_message("Card found")

        # Get signed identification from the fingerprint sensor
        self.display.draw_message("Scan fingerprint")
        fingerprint_match, fingerprint_id, fingerprint_message, fingerprint_message_signature = self.fingerprint.identify()
        self.display.draw_message("Fingerprint scanned")

        # Generate a new encryption key and seal it in the TPM
        encryption.Encryption.generate_and_seal_key(rfid_passcode, fingerprint_message, fingerprint_message_signature)


        # Encrypt the file system with the key
        encryption.Encryption.encrypt(rfid_passcode, fingerprint_message, fingerprint_message_signature)

        # Delete the plaintext file system image
        storage.delete_fs_image()

        self.display.draw_message("Reset complete!")
        print("# Reset complete!")
        time.sleep(1)


def main():
    m = Main()
    m.start()

if __name__ == "__main__":
    main()