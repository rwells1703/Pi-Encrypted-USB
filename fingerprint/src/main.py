#!/usr/bin/env python3

from bep import util
from bep.bep_extended import BepExtended
from bep.com_phy import ComPhy

def main():
    # Enable logging to the console
    util.setup_logging()

    # Use the raspberry pi SPI ports
    interface = "rpispi"

    # Establish a connection
    phy = ComPhy(interface)
    assert phy.connect(timeout=20)
    
    # Instantiate the BEP command interface
    bep_interface = BepExtended(phy)

    # Run commands
    run(bep_interface)

    # Close the connection
    phy.close()

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