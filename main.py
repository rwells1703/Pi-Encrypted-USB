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

    def start(self):
        os.chdir("/home/pi/piusb")

        # Delete any old USB gadget files that may be left over (e.g. the help drive or a fs left from a program crash)
        # logs are not shown because it will display error messages, during normal functionality
        # (ie. it will attempt to delete files that already exist)
        storage.remove_usb_gadget(False)
        storage.delete_fs_image(False)
        storage.unmount_tmpfs(False)
        
        # Runs the "stop" function when the program closes (e.g. if user presses ctrl+c)
        signal.signal(signal.SIGINT, self.close)

        self.tpm = encryption.TPM()
        self.tpm.restart()
        
        self.fingerprint = fingerprint.Fingerprint()

        self.reset_auth_details()

        self.mounted = False

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

    def reset_auth_details(self):
        self.rfid_passcode = None
        self.fingerprint_match = None
        self.fingerprint_message = None
        self.fingerprint_message_signature = None

    def authorize(self, message, action):
        valid = False
        tries = 5
        while not valid:
            # If the user has run out of tries to enter
            if tries == 0:
                self.display.draw_message("Out of tries,\nshutting down...")
                time.sleep(2)
                self.poweroff()

            # Get the passcode from the RFID card
            self.display.draw_message("Tap card")
            self.rfid_passcode = rfid.read_card_passcode(message)
            self.display.draw_message("Card found")
            time.sleep(1)

            # Get signed identification from the fingerprint sensor
            self.display.draw_message("Scan fingerprint")
            self.fingerprint_match, self.fingerprint_message, self.fingerprint_message_signature = self.fingerprint.identify()

            # If the fingerprint was found, move onto the next stage of authentication
            if self.fingerprint_match:
                self.display.draw_message("Fingerprint\nscanned")
                time.sleep(1)
                self.display.draw_message(message)

                valid = action(self.rfid_passcode, self.fingerprint_message, self.fingerprint_message_signature)
                if valid:
                    print("# Complete")
                    self.display.draw_message("Complete")
                    time.sleep(1)

                    return
        
            # Otherwise, the authorisation was invalid  
            tries -= 1

            # Provide a warning message
            self.display.draw_message(f"Incorrect\n{tries} tries left\nbefore shutdown")
            time.sleep(1)

    # Mount the storage drive, so it appears on the host computer
    def mount(self):
        if self.mounted:
            self.display.draw_message("Already mounted!")
            print("# Already mounted!")
        else:
            storage.mount_tmpfs()

            # Authorize and decrypt the drive
            self.authorize("Decrypting...", encryption.Encryption.decrypt)

            if config.AUTH_ON_EJECT:
                # Clear the authentication variables
                self.reset_auth_details()

            # Unmounts help drive if required
            storage.remove_usb_gadget(False)

            # The new USB gadget files are then created
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
            if config.AUTH_ON_EJECT:
                # Authorize and encrypt the drive
                self.authorize("Encrypting...", encryption.Encryption.encrypt)
            else:
                # Encrypt the drive using authorization values used to mount it
                self.display.draw_message("Encrypting...")
                encryption.Encryption.encrypt(self.rfid_passcode, self.fingerprint_message, self.fingerprint_message_signature)

            # Clear the authentication variables
            self.reset_auth_details()

            # The new USB gadget files are deleted
            storage.remove_usb_gadget()
            
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
        self.display.draw_message("Resetting...")

        # Remove any existing USB drives before resetting (this forces the host to eject)
        storage.remove_usb_gadget(False)
        
        self.mounted = False
        
        # Reset the TPM to blank
        self.tpm.reset()

        # Generate encrytion keys for communicating with fingerprint sensor
        encryption.Encryption.generate_fingerprint_communication_keys()

        storage.mount_tmpfs()

        # Create a new file system image
        storage.create_fs_image()

        self.display.draw_message("Tap card")
        rfid.reset_card_passcode()
        self.display.draw_message("Card reset")
        time.sleep(1)

        # Enroll the new fingerprint
        self.fingerprint.enroll(self.display)
        self.display.draw_message("Enrollment\ncomplete")
        time.sleep(1)

        # Authorize and decrypt the drive
        self.authorize("Generating key\n and encrypting...", encryption.Encryption.encrypt_new)

        if config.AUTH_ON_EJECT:
            # Clear the authentication variables
            self.reset_auth_details()

        # Delete the plaintext file system image
        storage.delete_fs_image()

        self.display.draw_message("Reset complete!")
        print("# Reset complete!")
        time.sleep(1)

def main():
    try:
        m = Main()
        m.start()
    except AssertionError:
        print("# CRC error occured, restarting.")
        main()

if __name__ == "__main__":
    main()