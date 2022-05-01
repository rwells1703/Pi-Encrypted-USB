#!/usr/bin/env python3

import time
import subprocess
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
        signal.signal(signal.SIGINT, self.stop)

        self.tpm = encryption.TPM()
        self.tpm.restart()

        storage.create_usb_gadget_help()

    def stop(self, sig=None, frame=None):
        storage.remove_usb_gadget(False)
        storage.delete_fs_image(False)
        storage.unmount_tmpfs(False)

        self.display.stop()

        self.tpm.stop()

        exit()

    def start_gui(self):
        self.display = display.Display()
        self.display.draw_menu(self.main_menu, "Main Menu")

    # Mount the storage drive, so it appears on the host computer
    def mount(self):
        if self.mounted:
            self.display.draw_message("Already mounted!")
            print("# Already mounted!")
        else:
            self.display.draw_message("Mounting...")

            storage.mount_tmpfs()

            self.display.draw_message("Tap card")
            self.rfid_passcode = rfid.read_card_passcode("decryption")
            self.display.draw_message("Card found")

            encryption.Encryption.decrypt(self.rfid_passcode)

            if config.INCREASED_SECURITY:
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

            if config.INCREASED_SECURITY:
                self.display.draw_message("Tap card")
                self.rfid_passcode = rfid.read_card_passcode("encryption")
                self.display.draw_message("Card found")

            storage.remove_usb_gadget()

            encryption.Encryption.encrypt(self.rfid_passcode)
            
            if config.INCREASED_SECURITY:
                self.rfid_passcode = None

            storage.unmount_tmpfs()

            self.mounted = False

            self.display.draw_message("Drive ejected!")
            print("# Drive ejected!")
        time.sleep(1)

    def poweroff(self):
        self.stop()
        #utils.execute_command(["poweroff"])

    # Reset the device to a new blank state
    def reset(self):       
        self.display.draw_message("Resetting..")

        # Remove any existing USB drives before resetting (this forces the host to eject)
        storage.remove_usb_gadget()
        
        self.mounted = False
        
        # Reset the TPM to blank
        self.tpm.reset()

        # Create a new file system image
        storage.create_fs_image()

        # Prompt the user to tap the RFID card
        self.display.draw_message("Tap card")
        # Generate a new passcode and write it to the RFID card
        rfid_passcode = rfid.reset_card_passcode()
        self.display.draw_message("Card found")

        # Generate a new encryption key and encrypt the file system with it
        encryption.Encryption.generate_key(rfid_passcode)
        encryption.Encryption.encrypt(rfid_passcode)

        # Delete the plaintext file system image
        storage.delete_fs_image()

        self.display.draw_message("Reset complete!")
        print("# Reset complete!")
        time.sleep(1)


def main():
    m = Main()

    m.start()
    m.start_gui()
    m.stop()

def debug():
    m = Main()
    m.start()

    storage.mount_drive()
    rfid.wait_for_card()
    storage.eject_drive()

    m.stop()

if __name__ == "__main__":
    main()