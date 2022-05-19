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
        self.phy = ComPhy(interface)
        assert self.phy.connect()
        
        # Instantiate the BEP command interface
        self.bep_interface = BepExtended(self.phy)

    def stop(self):
        # Close the connection
        self.phy.close()

    def enroll(self, display):
        # Remove any old saved fingerprints
        self.bep_interface.template_remove_all_flash()

        # Enroll the fingerprint
        self.bep_interface.enroll_start()
        
        enrollments_left = 3
        while enrollments_left != 0:
            display.draw_message(f"Scan fingerprint\n{enrollments_left} more\ntimes")
            self.bep_interface.capture()
            enrollments_left = self.bep_interface.enroll()

        self.bep_interface.enroll_finish()

        # Save the fingerprint as id 0
        self.bep_interface.template_save(0)

        self.bep_interface.template_remove_ram()

    def identify(self):
        # Capture and identify the fingerprint
        self.bep_interface.capture()
        self.bep_interface.image_extract()
        identity = self.bep_interface.identify()

        self.bep_interface.template_remove_ram()

        return identity[0], identity[2], identity[3]

    def clear_flash(self):
        # Clear the flash storage
        self.bep_interface.storage_format()