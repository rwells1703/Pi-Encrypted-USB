#!/usr/bin/env python3

import time
import subprocess
import os

import rfid
import utils
import encryption
import storage
import fingerprint

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
    fingerprint.example.main()

if __name__ == "__main__":
    test()