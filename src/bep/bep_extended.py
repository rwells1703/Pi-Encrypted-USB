# Copyright (c) 2020 Fingerprint Cards AB
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Extended bep functions"""

import logging
import time

from .bep import Bep


class BepExtended(Bep):
    """Extend BEP class with combined commands"""

    def capture_and_extract(self):
        """Capture and Extract"""
        self.capture(timeout_ms=(self.serial.timeout - 1) * 1000)
        self.image_extract()

    def capture_and_identify(self):
        """Capture, Extract, Identify, Clean-up"""
        self.capture(timeout_ms=(self.serial.timeout - 1) * 1000)
        self.image_extract()
        self.identify()
        time.sleep(1)
        self.template_remove_ram()

    def capture_and_enroll(self):
        """Capture and Enroll"""
        self.capture(timeout_ms=(self.serial.timeout - 1) * 1000)
        enrollments_left = self.enroll()
        return enrollments_left

    def enroll_finger(self):
        """Enroll finger"""
        self.enroll_start()

        while True:
            logging.info("")
            enrollments_left = self.capture_and_enroll()

            if enrollments_left == 0:
                break

            self.sensor_wait_finger_not_present(0)

        logging.info("")

        self.enroll_finish()
        logging.info("Finger enrolled")

    def template_save_and_release(self, idx=-1):
        """Save template to flash and release template"""
        self.template_save(idx)
        self.template_remove_ram()

    def template_get_and_release(self):
        """Receive template kept in RAM and release template"""
        template = self.template_get()
        self.template_remove_ram()
        return template
