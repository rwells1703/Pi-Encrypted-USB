import utils
import encryption

def create_fs_image():
    print("# STARTED create fs image")
    stdout = utils.execute_command(["./storage/scripts/create_fs_image"])
    print("# FINISHED create fs image")

def delete_fs_image():
    stdout = utils.execute_command(["./storage/scripts/delete_fs_image"])
    print("# Deleted fs image")


def mount_drive():
    mount_tmpfs()
    encryption.decrypt()
    create_usb_gadget()
    print("# Drive mounted")

def eject_drive():
    remove_usb_gadget()
    encryption.encrypt()
    unmount_tmpfs()
    print("# Drive ejected")


def mount_tmpfs():
    stdout = utils.execute_command(["mount","tmpfs","./storage/ramdisk","-t","tmpfs","-o","size=100M"])
    print("# Mounted tmpfs")

def unmount_tmpfs():
    stdout = utils.execute_command(["umount","./storage/ramdisk"])
    print("# Unmounted tmpfs")


def create_usb_gadget():
    stdout  = utils.execute_command(["./storage/scripts/create_usb_gadget"])
    print("# Created USB gadget for storage drive")

def remove_usb_gadget():
    stdout = utils.execute_command(["./storage/scripts/remove_usb_gadget"])
    print("# Removed USB gadget for storage drive")