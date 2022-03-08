#!/usr/bin/env python3

import time
import subprocess
import os

def main():
    startup()

# Set up the device from new
def initial_setup():
    generate_key()
    create_fs_image()
    encrypt()
    delete_fs_image()

def generate_key():
    pass

def create_fs_image():
    pass

def delete_fs_image():
    pass


# When the device first starts
def startup():
    disable_led_trigger()
    led_off()


    mount_help_drive()

    read_card_passcode()
    led_flicker()
    time.sleep(1)

    eject_help_drive()


    mount_main_drive()

    read_card_passcode()
    led_flicker()
    time.sleep(1)

    eject_main_drive()

    '''while True:
        led_on()
        time.sleep(0.5)
        led_off()
        time.sleep(0.5)'''

    execute_command(["poweroff"])

def mount_help_drive():
    create_usb_gadget_help()
    print("HELP DRIVE MOUNTED")

def eject_help_drive():
    remove_usb_gadget()
    print("HELP DRIVE EJECTED")

def mount_main_drive():
    mount_tmpfs()
    decrypt()
    create_usb_gadget_main()
    print("MAIN DRIVE MOUNTED")

def eject_main_drive():
    remove_usb_gadget()
    encrypt()
    unmount_tmpfs()
    print("MAIN DRIVE EJECTED")


def mount_tmpfs():
    stdout, stderr = execute_command(["mount","tmpfs","/home/pi/piusb/storage/ramdisk","-t","tmpfs","-o","size=100M"])
    print("MOUNTED TEMPORARY FILE SYSTEM (TMPFS)")

def unmount_tmpfs():
    stdout, stderr = execute_command(["umount","/home/pi/piusb/storage/ramdisk"])
    print("UNMOUNTED TEMPORARY FILE SYSTEM (TMPFS)")


def create_usb_gadget_help():
    stdout, stderr = execute_command(["/home/pi/piusb/storage/create_usb_gadget_help"])
    print("CREATED USB GADGET HELP")

def create_usb_gadget_main():
    stdout, stderr = execute_command(["/home/pi/piusb/storage/create_usb_gadget_main"])
    print("CREATED USB GADGET MAIN")

def remove_usb_gadget():
    stdout, stderr = execute_command(["/home/pi/piusb/storage/remove_usb_gadget"])
    print("REMOVED USB GADGET")


def decrypt():
    led_on()
    passcode = read_card_passcode()
    led_off()

    print("(STARTED) DECRYTING FILE SYSTEM")
    stdout, stderr = execute_command(["/home/pi/piusb/encryption/decrypt_fs", passcode])
    print("(COMPLETED) DECRYTING FILE SYSTEM")

def encrypt():
    led_on()
    passcode = read_card_passcode()
    led_off()

    print("(STARTED) ENCRYPTING FILE SYSTEM")
    stdout, stderr = execute_command(["/home/pi/piusb/encryption/encrypt_fs", passcode])
    print("(COMPLETED) ENCRYPTING FILE SYSTEM")


def read_card_passcode():
    print("(STARTED) READ CARD PASSCODE")
    stdout, stderr = execute_command(["/home/pi/piusb/rfid/src/read_card.out"])
    print("(COMPLETED) READ CARD PASSCODE")

    # Converts passcode from bytestring to utf-8 string
    passcode = stdout.decode("utf-8")

    # Strips new line characters and null bytes from the output string
    passcode = passcode.rstrip("\r\n").rstrip("\x00")
    return passcode


def execute_command(command):
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()

    return stdout, stderr


def disable_led_trigger():
    execute_command(["sh", "-c", "\"echo", "none", ">", "/sys/class/leds/led0/trigger\""])

def led_on():
    #execute_command(["sh", "-c", "echo", "1", ">", "/sys/class/leds/led0/brightness"])
    os.system("sh -c \"echo 1 > /sys/class/leds/led0/brightness\"")

def led_off():
    #execute_command(["sh", "-c", "echo", "0", ">", "/sys/class/leds/led0/brightness"])
    os.system("sh -c \"echo 0 > /sys/class/leds/led0/brightness\"")

def led_flicker():
    led_on()
    led_off()


if __name__ == "__main__":
    main()
