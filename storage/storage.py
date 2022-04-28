import utils
import encryption

def create_fs_image():
    print("# STARTED create fs image")

    stdout = utils.execute_command(["./storage/scripts/create_fs_image"])

    print("# FINISHED create fs image")

def delete_fs_image():
    stdout = utils.execute_command(["./storage/scripts/delete_fs_image"])

    print("# Deleted fs image")


def mount_help_drive():
    create_usb_gadget_help()
    print("# HELP drive mounted")

def eject_help_drive():
    remove_usb_gadget("HELP")
    print("# HELP drive ejected")


def mount_main_drive():
    mount_tmpfs()
    encryption.decrypt()
    create_usb_gadget_main()
    print("# MAIN drive mounted")

def eject_main_drive():
    remove_usb_gadget("MAIN")
    encryption.encrypt()
    unmount_tmpfs()
    print("# MAIN drive ejected")


def mount_tmpfs():
    stdout = utils.execute_command(["mount","tmpfs","/home/pi/piusb/storage/ramdisk","-t","tmpfs","-o","size=100M"])
    print("# Mounted tmpfs")

def unmount_tmpfs():
    stdout = utils.execute_command(["umount","/home/pi/piusb/storage/ramdisk"])
    print("# Unmounted tmpfs")


def create_usb_gadget_help():
    stdout = utils.execute_command(["./storage/scripts/create_usb_gadget_help"])
    print("# Created USB gadget for HELP drive")

def create_usb_gadget_main():
    stdout  = utils.execute_command(["./storage/scripts/create_usb_gadget_main"])
    print("# Created USB gadget for MAIN drive")

def remove_usb_gadget(drive_name):
    stdout = utils.execute_command(["./storage/scripts/remove_usb_gadget"])
    print("# Removed USB gadget for " + drive_name + " drive")