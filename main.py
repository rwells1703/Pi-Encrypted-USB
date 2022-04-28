#!/usr/bin/env python3

import time
import subprocess
import os

import rfid
import utils
import encryption
import storage

# Set up the device from new
def initial_setup():
    encryption.generate_card_password()
    storage.create_fs_image()
    tpm_server_proc = encryption.start_tpm()
    encryption.reset_tpm()
    encryption.generate_key()
    encryption.encrypt()
    encryption.stop_tpm(tpm_server_proc)
    storage.delete_fs_image()

# When the device first starts
def main():
    utils.disable_led_trigger()
    utils.led_off()

    '''storage.mount_help_drive()

    rfid.wait_for_card()
    utils.led_flicker()

    storage.eject_help_drive()

    time.sleep(0.5)'''

    tpm_server_proc = encryption.start_tpm()

    storage.mount_main_drive()

    rfid.wait_for_card()
    utils.led_flicker()
    time.sleep(1)

    storage.eject_main_drive()

    encryption.stop_tpm(tpm_server_proc)



    '''while True:
        utils.led_on()
        time.sleep(0.5)
        utils.led_off()
        time.sleep(0.5)'''

    #utils.execute_command(["poweroff"])

    print("# END")

if __name__ == "__main__":
    main()