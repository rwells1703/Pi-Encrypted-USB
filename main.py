#!/usr/bin/env python3

import time
import subprocess
import os

def main():
    startup()

# Set up the device from new
def initial_setup():
    generate_card_password()
    create_fs_image()
    tpm_server_proc = start_tpm()
    reset_tpm()
    generate_key()
    encrypt()
    stop_tpm(tpm_server_proc)
    delete_fs_image()

def generate_card_password():
    pass

def generate_key():
    passcode = read_card_passcode("key generation")

    print("# STARTED generate AES key")

    stdout = execute_command(["/home/pi/piusb/encryption/generate_key", passcode])
    print(stdout.decode("utf-8"))
    
    print("# FINISHED generate AES key")

def create_fs_image():
    print("# STARTED create fs image")

    stdout = execute_command(["/home/pi/piusb/storage/create_fs_image"])
    print(stdout.decode("utf-8"))

    print("# FINISHED create fs image")

def delete_fs_image():
    stdout = execute_command(["/home/pi/piusb/storage/delete_fs_image"])
    print(stdout.decode("utf-8"))

    print("# Deleted fs image")


# When the device first starts
def startup():
    disable_led_trigger()
    led_off()

    '''mount_help_drive()

    wait_for_card()
    led_flicker()
    time.sleep(1)

    eject_help_drive()
    print()
    exit()'''

    tpm_server_proc = start_tpm()

    mount_main_drive()

    wait_for_card()
    led_flicker()
    time.sleep(1)

    eject_main_drive()

    stop_tpm(tpm_server_proc)

    print("# END")

    while True:
        led_on()
        time.sleep(0.5)
        led_off()
        time.sleep(0.5)

    #execute_command(["poweroff"])

def mount_help_drive():
    create_usb_gadget_help()
    print("# HELP drive mounted")

def eject_help_drive():
    remove_usb_gadget("HELP")
    print("# HELP drive ejected")


def get_tpm_shell_env():
    # Specify the host and port for the TPM server
    env = os.environ.copy()
    env["TPM2TOOLS_TCTI"] = "mssim:host=localhost,port=2321"
    
    return env

def start_tpm():
    # Start the TPM server
    tpm_server_proc = subprocess.Popen(["/home/pi/piusb/encryption/stpm/src/tpm_server"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

    try:
        # The 1 second pause also gives the TPM server to start properly
        # TODO: Replace this long pause with checks on the output of the "startup -c" command to see if there is an error
        # iF there is an error, wait and then retry till the server is ready
        stdout, stderr = tpm_server_proc.communicate(timeout=1)
    except subprocess.TimeoutExpired:
        # This should occur if the TPM server started properly
        # as there should be no end-of-file character yet
        pass
    else:
        # There has been an error as the TPM server has already stopped
        print(stdout.decode("utf-8"))

    print("# TPM started")

    return tpm_server_proc

def stop_tpm(tpm_server_proc):
    tpm_server_proc.kill()

def clear_tpm_nv():
    stdout = execute_command(["/home/pi/piusb/encryption/clear_tpm_nv"])
    print(stdout.decode("utf-8"))

    print("TPM NV RAM has been cleared")

def reset_tpm():
    stdout = execute_command(["/home/pi/piusb/encryption/reset_tpm"])
    print(stdout.decode("utf-8"))

    print("# TPM has been reset")


def mount_main_drive():
    mount_tmpfs()
    decrypt()
    create_usb_gadget_main()
    print("# MAIN drive mounted")

def eject_main_drive():
    remove_usb_gadget("MAIN")
    encrypt()
    unmount_tmpfs()
    print("# MAIN drive ejected")


def mount_tmpfs():
    stdout = execute_command(["mount","tmpfs","/home/pi/piusb/storage/ramdisk","-t","tmpfs","-o","size=100M"])
    print("# Mounted tmpfs")

def unmount_tmpfs():
    stdout = execute_command(["umount","/home/pi/piusb/storage/ramdisk"])
    print("# Unmounted tmpfs")


def create_usb_gadget_help():
    stdout = execute_command(["/home/pi/piusb/storage/create_usb_gadget_help"])
    print("# Created USB gadget for HELP drive")

def create_usb_gadget_main():
    stdout  = execute_command(["/home/pi/piusb/storage/create_usb_gadget_main"])
    print("# Created USB gadget for MAIN drive")

def remove_usb_gadget(drive_name):
    stdout = execute_command(["/home/pi/piusb/storage/remove_usb_gadget"])
    print("# Removed USB gadget for " + drive_name + " drive")


def decrypt():
    passcode = read_card_passcode("decryption")

    print("# STARTED decrypting file system")
    stdout = execute_command(["/home/pi/piusb/encryption/decrypt", passcode])
    print(stdout.decode("utf-8"))
    
    print("# FINISHED decrypting file system")

def encrypt():
    passcode = read_card_passcode("encryption")

    print("# STARTED encrypting file system")
    stdout = execute_command(["/home/pi/piusb/encryption/encrypt", passcode])
    print(stdout.decode("utf-8"))
    
    print("# FINISHED encrypting file system")


def read_card_passcode(reason):
    led_on()

    print("# Waiting for RFID card containing password for " + reason)
    stdout = execute_command(["/home/pi/piusb/rfid/src/read_card.out"])
    print("# Card password read")

    led_off()

    # Converts passcode from bytestring to utf-8 string
    passcode = stdout.decode("utf-8")

    # Strips new line characters and null bytes from the output string
    passcode = passcode.rstrip("\r\n").rstrip("\x00")
    return passcode

def wait_for_card():
    print("# Waiting for RFID card tap")
    stdout = execute_command(["/home/pi/piusb/rfid/src/read_card.out"])
    print("# Card found")


def execute_command(command):
    process = subprocess.Popen(command, env=get_tpm_shell_env() ,stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    stdout, stderr = process.communicate()

    return stdout


def disable_led_trigger():
    subprocess.run("sh -c \"echo none > /sys/class/leds/led0/trigger\"", shell=True)

def led_on():
    subprocess.run("sh -c \"echo 1 > /sys/class/leds/led0/brightness\"", shell=True)

def led_off():
    subprocess.run("sh -c \"echo 0 > /sys/class/leds/led0/brightness\"", shell=True)

def led_flicker():
    led_on()
    led_off()


if __name__ == "__main__":
    main()