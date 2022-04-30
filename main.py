#!/usr/bin/env python3

import time
import subprocess
import os

import rfid
import utils
import encryption
import storage
import fingerprint
import display

class Main:
    def __init__(self):
        self.main_menu = {
            "Mount": self.mount,
            "More": self.more,
            "Poweroff": self.poweroff
        }

        self.more_menu = {
            "Format drive": self.format_drive,
            "Change fingerprint": self.change_fingerprint,
            "Change card": self.change_card,
            "Change master psk": self.change_master_psk,
            "Factory reset": self.factory_reset,
            "Back": self.back
        }

    def initialise(self):
        os.chdir("/home/pi/piusb")
        
        utils.disable_led_trigger()
        utils.led_off()

        self.tpm = encryption.TPM()
        self.tpm.restart()

    def finish(self):
        self.tpm.stop()
        print("# END")

    def start_gui(self):
        self.display = display.Display()
        self.display.draw_menu(self.main_menu, "Main Menu")

    # Reset the device to a new blank state
    def reset(self):
        # Generate a new passcode to store on the RFID card
        encryption.generate_card_passcode()

        # Create a new file system image
        storage.create_fs_image()

        # Reset the TPM to blank
        self.tpm.reset()

        # Generate a new encryption key and encrypt the file system with it
        encryption.generate_key()
        encryption.encrypt()

        # Delete the plaintext file system image
        storage.delete_fs_image()


    def mount(self):
        self.display.draw_message("Tap card")
        storage.mount_drive()
        self.display.draw_message("Mounted!")
        time.sleep(1)

    def more(self):
        self.display.draw_menu(self.more_menu, "More Menu")

    def poweroff(self):
        print("nooooo the power is out")
        #utils.execute_command(["poweroff"])
        exit()

    def back(self):
        return True

    def format_drive(self):
        print("the drive has been factory reset")

    def change_fingerprint(self):
        print("new fingerprint please")

    def change_card(self):
        print("tap new card please")

    def change_master_psk(self):
        print("enter new psk please")

    def factory_reset(self):
        print("completely reset")


def main():
    m = Main()

    m.initialise()
    m.start_gui()
    m.finish()

def debug():
    m = Main()
    m.initialise()

    storage.mount_drive()
    rfid.wait_for_card()
    storage.eject_drive()

    m.finish()

if __name__ == "__main__":
    main()