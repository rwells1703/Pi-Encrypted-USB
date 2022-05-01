import utils
import encryption

# Creates an image file containing the file system of the specified size
# Max size 1024M (defined below as ramdisk size)
def create_fs_image(block_size="1M", count="64", show_log=True):
    print("# STARTED create fs image")
    stdout = utils.execute_command(["./storage/scripts/create_fs_image", block_size, count], show_log)
    print("# FINISHED create fs image")

# Delete the file system image (used during reset)
def delete_fs_image(show_log=True):
    stdout = utils.execute_command(["./storage/scripts/delete_fs_image"], show_log)
    print("# Deleted fs image")

# Create a temporary ramdisk for storing the file system while it is mounted
# Size of 1024M (limited by onboard RAM size, otherwise may rely on insecure swap files)
def mount_tmpfs(show_log=True):
    remove_usb_gadget(False)
    unmount_tmpfs(False)
    stdout = utils.execute_command(["./storage/scripts/mount_tpmfs","1024M"], show_log)
    print("# Mounted tmpfs")

# Delete the ramdisk
def unmount_tmpfs(show_log=True):
    stdout = utils.execute_command(["./storage/scripts/unmount_tpmfs"], show_log)
    print("# Unmounted tmpfs")

# Create a linux kernel gadget for a USB storage device in the /sys/ folder
def create_usb_gadget(show_log=True):
    stdout  = utils.execute_command(["./storage/scripts/create_usb_gadget"], show_log)
    print("# Created USB gadget for storage drive")

# Delete the linux kernel gadget for a USB storage device
def remove_usb_gadget(show_log=True):
    stdout = utils.execute_command(["./storage/scripts/remove_usb_gadget"], show_log)
    print("# Removed USB gadget for storage drive")