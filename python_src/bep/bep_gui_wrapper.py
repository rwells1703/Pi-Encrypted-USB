#!/usr/bin/env python3

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

"""BEP core functions"""

import logging
import struct

from bep import util
from bep.bep import Bep
from .communication import Command, Argument, Com


class BepGUIWrapper(Bep):
    # pylint: disable = R0904
    """Class to extend BEP interface for GUI functionality"""

    def __init__(self, serial):
        self.serial = serial

    def image_get(self, display=True, callback=None):
        """Get the image and show it"""
        image = b''
        image_width = 0
        image_height = 0

        if callback:
            callback(text="Place finger on sensor")

        self.capture()

        com = Com(Command.CMD_IMAGE, Argument.ARG_UPLOAD)
        com.transceive(self.serial)

        if Argument.ARG_WIDTH in com.keys_rx:
            image_width = com.get_as_uint(Argument.ARG_WIDTH)
            logging.info("Got width %d", image_width)
        if Argument.ARG_HEIGHT in com.keys_rx:
            image_height = com.get_as_uint(Argument.ARG_HEIGHT)
            logging.info("Got height %d", image_height)
        if Argument.ARG_DATA in com.keys_rx:
            image = com.keys_rx[Argument.ARG_DATA]
            logging.info("Total image size %s", len(image))
            if callback:
                callback(progress=len(image), max_progress=image_width * image_height)
        else:
            return False, image

        com.check_result()

        util.convert_image(image, display=display, width=image_width, height=image_height)

        return True, image

    def enroll(self, callback=None):
        """Enroll image"""
        max_enrollments = 0

        self.enroll_start()

        while True:
            if callback:
                callback(text="Place finger on sensor")
            self.capture()
            enrollments_left = super().enroll()
            if enrollments_left == 0:
                break
            if max_enrollments == 0:
                max_enrollments = enrollments_left + 1

            logging.info("Image enrolled, %i captures left", enrollments_left)
            if callback:
                callback(text='Image enrolled, {} captures left'.format(enrollments_left),
                         progress=max_enrollments - enrollments_left,
                         max_progress=max_enrollments)

            self.sensor_wait_finger_not_present(0)

        self.enroll_finish()

        id = self.template_get_count() + 1
        self.template_save(id)
        logging.info("Finger enrolled")

        return True

    def identify(self, callback=None):
        """Send identify request"""
        if callback:
            callback(text="Place finger on sensor")
        self.capture()
        self.image_extract()
        match, match_id = super().identify()

        if not match:
            if callback:
                callback(text="Identify: no match", match=False)
        else:
            if callback:
                callback(text='Identify: match against id {}'.format(match_id), match=True)

        return True

    def template_remove_all_flash(self):
        """Remove all templates from flash"""
        super().template_remove_all_flash()

        return True
