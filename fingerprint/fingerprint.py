#!/usr/bin/env python3

import encryption

from fingerprint.bep import util
from fingerprint.bep.bep_extended import BepExtended
from fingerprint.bep.com_phy import ComPhy

class Fingerprint:
    def __init__(self):
        self.start()
        self.run()
        self.stop()

    def start(self):
        # Enable logging to the console
        util.setup_logging()

        # Use the raspberry pi SPI ports
        interface = "rpispi"

        # Establish a connection
        com = ComPhy(interface)
        assert com.connect(timeout=20)
        
        # Instantiate the BEP command interface
        self.bep_interface = BepExtended(com)

    def stop(self):
        # Close the connection
        com.close()

    def run(self):
        self.bep_interface.version_get()

        # Clear the flash storage
        #bep_interface.storage_format()

        # Get the number of templates
        template_count = self.bep_interface.template_get_count()

        # Enroll the fingerprint
        self.bep_interface.enroll_finger()
        self.bep_interface.template_save(template_count)
        self.bep_interface.template_remove_ram()

        # Identify the fingerprint
        self.bep_interface.capture()
        self.bep_interface.image_extract()
        self.bep_interface.identify()