#!/usr/bin/env python3

from fingerprint.bep import util
from fingerprint.bep.bep_extended import BepExtended
from fingerprint.secure_com_wrapper import ComSecure

def main():
    # Enable logging to the console
    util.setup_logging()

    # Use the raspberry pi SPI ports
    interface = "rpispi"

    # Establish a connection
    com = ComSecure(interface)
    assert com.connect(timeout=20)
    
    # Instantiate the BEP command interface
    bep_interface = BepExtended(com)

    # Run commands
    run(bep_interface)

    # Close the connection
    com.close()

def run(bep_interface):
    bep_interface.version_get()

    # Clear the flash storage
    #bep_interface.storage_format()

    # Get the number of templates
    template_count = bep_interface.template_get_count()

    # Enroll the fingerprint
    bep_interface.enroll_finger()
    bep_interface.template_save(template_count)
    bep_interface.template_remove_ram()

    # Identify the fingerprint
    bep_interface.capture()
    bep_interface.image_extract()
    bep_interface.identify()

if __name__ == "__main__":
    main()