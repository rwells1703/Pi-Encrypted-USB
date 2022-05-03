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
        com = ComPhy(interface)
        assert com.connect()
        
        # Instantiate the BEP command interface
        self.bep_interface = BepExtended(com)

    def stop(self):
        # Close the connection
        com.close()

    def enroll(self):
        # Enroll the fingerprint
        self.bep_interface.enroll_finger()

        # Save the fingerprint as id 0
        self.bep_interface.template_save(0)
        self.bep_interface.template_remove_ram()

    def identify(self):
        completed = False
        while not completed:
            try:
                # Capture and identify the fingerprint
                self.bep_interface.capture()
                self.bep_interface.image_extract()
                response = self.bep_interface.identify()
                completed = True
                return response
            except AssertionError:
                print("# CRC Check failed, trying again")

    def clear(self):
        # Clear the flash storage
        bep_interface.storage_format()