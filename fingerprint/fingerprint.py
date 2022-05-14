#!/usr/bin/env python3

import encryption

from fingerprint.bep import util
from fingerprint.bep.bep_extended import BepExtended
from fingerprint.bep.com_phy import ComPhy

class Fingerprint:
    def __init__(self):
        self.start()

    def start(self):
        # Enable logging to the console
        util.setup_logging()

        # Use the raspberry pi SPI ports
        interface = "rpispi"

        # Establish a connection
        self.com = ComPhy(interface)
        assert self.com.connect(timeout=20)
        
        # Instantiate the BEP command interface
        self.bep_interface = BepExtended(self.com)

    def stop(self):
        # Close the connection
        self.com.close()

    def enroll(self):
        # Enroll the fingerprint
        self.bep_interface.enroll_finger()

        # Save the fingerprint as id 0
        self.bep_interface.template_save(0)
        self.bep_interface.template_remove_ram()

    def identify(self):
        # Capture and identify the fingerprint
        self.bep_interface.capture()
        self.bep_interface.image_extract()
        self.bep_interface.template_remove_ram()
        return self.bep_interface.identify()

    def clear_flash(self):
        # Clear the flash storage
        self.bep_interface.storage_format()