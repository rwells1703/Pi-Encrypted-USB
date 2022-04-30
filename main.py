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

# Set up the device from new
def initial_setup():
    os.chdir("/home/pi/piusb")

    encryption.generate_card_passcode()

    storage.create_fs_image()

    tpm = encryption.TPM()
    tpm.start()
    tpm.reset()

    encryption.generate_key()
    encryption.encrypt()

    tpm.stop()

    storage.delete_fs_image()

# When the device first starts
def main():
    os.chdir("/home/pi/piusb")
    
    utils.disable_led_trigger()
    utils.led_off()

    tpm = encryption.TPM()
    tpm.start()

    storage.mount_drive()

    rfid.wait_for_card()

    storage.eject_drive()

    tpm.stop()

    #utils.execute_command(["poweroff"])

    print("# END")

def test():
    def mount(device):
        print("yay the device is mounted")

    def more(device):
        d.draw_menu(more_menu, "More Menu")

    def poweroff(device):
        print("nooooo the power is out")
        exit()

    def back(device):
        return True

    def format_drive(device):
        print("the drive has been factory reset")

    def change_fingerprint(device):
        print("new fingerprint please")

    def change_card(device):
        print("tap new card please")

    def change_master_psk(device):
        print("enter new psk please")

    def factory_reset(device):
        print("completely reset")

    main_menu = {
        "Mount": mount,
        "More": more,
        "Poweroff": poweroff
    }

    more_menu = {
        "Format drive": format_drive,
        "Change fingerprint": change_fingerprint,
        "Change card": change_card,
        "Change master psk": change_master_psk,
        "Factory reset": factory_reset,
        "Back": back
    }

    d = display.Display()
    d.draw_menu(main_menu, "Main Menu")

if __name__ == "__main__":
    test()