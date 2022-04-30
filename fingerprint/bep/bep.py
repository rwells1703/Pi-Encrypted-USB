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
import os
from collections import OrderedDict
from PIL import Image

from . import util
from .communication import Command, Argument, ProgramSpecificArgument

from fingerprint.secure_com_wrapper import ComSecure as Com

class BepTargetParameters(object):
    # pylint: disable = R0903
    """Class for handling of BEP target parameters """

    # SENSOR_TYPES - fpc_bep_sensor_type_t in fpc_bep_types.h
    SENSOR_TYPES = {
        "FPC1020": 1,
        "RESERVED1": 2,
        "FPC1320": 3,
        "FPC1321": 4,
        "FPC1025": 5,
        "FPC1075": 6,
        "FPC1035": 7,
    }
    SENSOR_TYPES_BY_VALUE = {v: k for k, v in SENSOR_TYPES.items()}

    # LOG_LEVELS - fpc_log_level_t in fpc_log.h
    LOG_LEVELS = {
        "FPC_LOG_LEVEL_ALERT": 0,
        "FPC_LOG_LEVEL_ERROR": 1,
        "FPC_LOG_LEVEL_WARNING": 2,
        "FPC_LOG_LEVEL_INFO": 3,
        "FPC_LOG_LEVEL_DEBUG": 4
    }
    LOG_LEVELS_BY_VALUE = {v: k for k, v in LOG_LEVELS.items()}

    # LOG_MODES
    LOG_MODES = {
        "FPC_LOG_MODE_UART": 0,
        "FPC_LOG_MODE_ITM": 1,
        "FPC_LOG_MODE_MEMORY": 2
    }
    LOG_MODES_BY_VALUE = {v: k for k, v in LOG_MODES.items()}

    # Enrollment feedback values
    ENROLLMENT_FEEDBACK = {
        "FPC_BEP_ENROLLMENT_DONE": 1,
        "FPC_BEP_ENROLLMENT_PROGRESS": 2,
        "FPC_BEP_ENROLLMENT_REJECT_REASON_LOW_QUALITY": 3,
        "FPC_BEP_ENROLLMENT_REJECT_REASON_LOW_SENSOR_COVERAGE": 4,
        "FPC_BEP_ENROLLMENT_REJECT_REASON_OTHER": 5
    }
    ENROLLMENT_FEEDBACK_BY_VALUE = {v: k for k, v in ENROLLMENT_FEEDBACK.items()}

    #Production test feedback values
    PROD_TEST_FEEDBACK = {
        "FPC_BEP_SENSOR_TEST_OK": 0,
        "FPC_BEP_SENSOR_TEST_FAILED": 1
    }
    PROD_TEST_FEEDBACK_BY_VALUE = {v: k for k, v in PROD_TEST_FEEDBACK.items()}

class Bep(object):
    # pylint: disable = R0904
    # pylint: disable = C0302
    # pylint: disable = R0913
    """Class to connect and communicate with BEP ref_app"""

    def __init__(self, serial):
        self.serial = serial

    def capture(self, max_tries=3, timeout_ms=0):
        """Capture an image"""
        tries = 0

        while True:
            logging.info("Place finger on sensor")

            com = Com(Command.CMD_CAPTURE)

            if timeout_ms != 0:
                # Send timeout_ms as uint16_t, 2 bytes
                com.add_arg(Argument.ARG_TIMEOUT, timeout_ms.to_bytes(2, byteorder='little'))

            com.transmit(self.serial)
            com.receive(self.serial)

            result = com.get_result()
            if result == 0:
                logging.info("Finger captured")
                break
            else:
                # Check for capture error
                assert result == -15, "Failure in capture function. Got result %d, %s" \
                                      % (result, com.result_to_string(result))
                assert tries < max_tries, "Max number of tries reached"
                tries += 1

    def capture_timeout(self):
        timeout_ms = int(input("Enter timeout in ms >> "))
        self.capture(timeout_ms=timeout_ms)

    def image_get_size(self):
        com = Com(Command.CMD_IMAGE, Argument.ARG_SIZE)
        com.transceive(self.serial)

        image_size = com.get_as_uint(Argument.ARG_SIZE)
        logging.info("Got image size %d", image_size)

        return image_size

    def image_create(self):
        """Allocates image buffer on target"""
        com = Com(Command.CMD_IMAGE, Argument.ARG_CREATE)
        com.transceive(self.serial)

    def image_delete(self):
        """Deletes image buffer on target"""
        com = Com(Command.CMD_IMAGE, Argument.ARG_DELETE)
        com.transceive(self.serial)

    def image_get(self):
        """Get the image and show it"""
        image_width = 0
        image_height = 0

        com = Com(Command.CMD_IMAGE, Argument.ARG_UPLOAD)
        com.transceive(self.serial)

        image = com.get_key_data(Argument.ARG_DATA)
        logging.info("Got image with size %s", len(image))
        if Argument.ARG_WIDTH in com.keys_rx:
            image_width = com.get_as_uint(Argument.ARG_WIDTH)
            logging.info("Got width %d", image_width)
        if Argument.ARG_HEIGHT in com.keys_rx:
            image_height = com.get_as_uint(Argument.ARG_HEIGHT)
            logging.info("Got height %d", image_height)

        try:
            util.convert_image(image, display=True, width=image_width, height=image_height)
        except NameError:
            pass

        return image

    def image_put(self, image=None):
        """Send image"""
        if not image:
            filename = input("Enter raw image file name>> ")
            _, ext = os.path.splitext(filename)
            if ext == '.raw':
                image = util.read_file(filename)
            else:
                try:
                    im = Image.open(filename, 'r')
                    image = bytes(im.getdata())
                except IOError:
                    logging.info("Could not open image file with format: %s", ext)
                    return

        self.image_create()

        image_size = self.image_get_size()
        assert image_size == len(image), "Image size doesn't match sensor size"

        com = Com(Command.CMD_IMAGE, Argument.ARG_DOWNLOAD)
        com.add_arg(Argument.ARG_DATA, image)
        com.transceive(self.serial)
        logging.info("Image sent successfully")

    def image_extract(self):
        com = Com(Command.CMD_IMAGE, Argument.ARG_EXTRACT)
        com.transceive(self.serial)
        logging.info("Image extracted")

    def enroll_start(self):
        """ Start enroll session """
        com = Com(Command.CMD_ENROLL, Argument.ARG_START)
        com.transceive(self.serial)
        logging.info("Enroll started")

    def enroll(self):
        """Enroll image"""
        com = Com(Command.CMD_ENROLL, Argument.ARG_ADD)
        com.transceive(self.serial)

        enrollments_left = com.get_as_uint(Argument.ARG_COUNT)
        feedback = com.get_as_uint(Argument.ARG_STATUS)

        assert feedback in BepTargetParameters.ENROLLMENT_FEEDBACK.values(), \
            "Invalid enrollment feedback (%d)!" % feedback
        if feedback <= BepTargetParameters.ENROLLMENT_FEEDBACK["FPC_BEP_ENROLLMENT_PROGRESS"]:
            logging.info("Image enrolled, %i enrollments left (%s)", enrollments_left,
                         BepTargetParameters.ENROLLMENT_FEEDBACK_BY_VALUE[feedback])
        else:
            logging.info("Failed to enroll image (%s), %i enrollments left",
                         BepTargetParameters.ENROLLMENT_FEEDBACK_BY_VALUE[feedback],
                         enrollments_left)
        return enrollments_left

    def enroll_finish(self):
        """ Finalize enroll session """
        com = Com(Command.CMD_ENROLL, Argument.ARG_FINISH)
        com.transceive(self.serial)
        logging.info("Enroll finished")

    def enroll_subtemplate_save(self, subtemplate_id=-1):
        if int(subtemplate_id) < 0:
            subtemplate_id = int(input("Enter flash storage item id (1000-1009)>> "))
        com = Com(Command.CMD_ENROLL, ProgramSpecificArgument.ARG_SUBTEMPLATE_SAVE)
        com.add_arg(Argument.ARG_ID, subtemplate_id.to_bytes(4, byteorder='little'))

        com.transceive(self.serial)
        logging.info("Subtemplate saved with id %s", subtemplate_id)

    def enroll_subtemplate_load(self):
        com = Com(Command.CMD_ENROLL, ProgramSpecificArgument.ARG_SUBTEMPLATE_LOAD)
        com.transceive(self.serial)
        logging.info("Subtemplates loaded")

    def identify(self, identify_template=None):
        """Send identify request"""
        match_id = -1
        com = Com(Command.CMD_IDENTIFY)
        if identify_template:
            com.add_arg(Argument.ARG_DATA, identify_template)

        com.transceive(self.serial)

        match = bool(com.get_as_uint(Argument.ARG_MATCH))
        if match:
            match_id = com.get_as_uint(Argument.ARG_ID)
            logging.info("Identify: match against id %s", match_id)
        else:
            logging.info("Identify: no match")
        return match, match_id

    def template_save(self, idx=-1):
        if int(idx) < 0:
            idx = int(input("Enter ID>> "))

        com = Com(Command.CMD_TEMPLATE, Argument.ARG_SAVE)
        com.add_arg(Argument.ARG_ID, idx.to_bytes(2, byteorder='little'))

        com.transceive(self.serial)
        logging.info("Template saved with id %s", idx)

    def template_remove_ram(self):
        com = Com(Command.CMD_TEMPLATE, Argument.ARG_DELETE)
        com.transceive(self.serial)
        logging.info("Template removed from RAM")

    def template_get(self):
        com = Com(Command.CMD_TEMPLATE, Argument.ARG_UPLOAD)
        com.transceive(self.serial)

        template = com.get_key_data(Argument.ARG_DATA)
        logging.info("Got template with size %s", len(template))
        return template

    def template_put(self, template):
        com = Com(Command.CMD_TEMPLATE, Argument.ARG_DOWNLOAD)
        com.add_arg(Argument.ARG_DATA, template)
        com.transceive(self.serial)

    def template_remove_flash(self, idx=-1):
        if idx < 0:
            idx = int(input("Enter ID>> "))

        com = Com(Command.CMD_STORAGE_TEMPLATE, Argument.ARG_DELETE)
        com.add_arg(Argument.ARG_ID, idx.to_bytes(2, byteorder='little'))

        com.transceive(self.serial)
        logging.info("Template with id %s removed", idx)

    def template_remove_all_flash(self):
        com = Com(Command.CMD_STORAGE_TEMPLATE, Argument.ARG_DELETE)
        com.add_arg(Argument.ARG_ALL)

        com.transceive(self.serial)
        logging.info("All templates removed")

    def template_load_from_flash(self, idx=-1):
        if idx < 0:
            idx = int(input("Enter ID>> "))

        com = Com(Command.CMD_STORAGE_TEMPLATE, Argument.ARG_UPLOAD)
        com.add_arg(Argument.ARG_ID, idx.to_bytes(2, byteorder='little'))

        com.transceive(self.serial)
        logging.info("Template loaded")

    def template_get_count(self):
        com = Com(Command.CMD_STORAGE_TEMPLATE, Argument.ARG_COUNT)
        com.transceive(self.serial)
        count = com.get_as_uint(Argument.ARG_COUNT)
        logging.info("There are %d templates in flash storage", count)
        return count

    def template_get_ids(self):
        com = Com(Command.CMD_STORAGE_TEMPLATE, Argument.ARG_ID)
        com.transceive(self.serial)

        ids = com.get_as_uint_list(Argument.ARG_DATA, '<H')
        logging.info("Template ids: %s", ", ".join(str(i) for i in ids))

        return ids

    def storage_format(self):
        """Format flash storage"""
        com = Com(Command.CMD_STORAGE, Argument.ARG_FORMAT)
        com.transceive(self.serial)
        logging.info("Flash storage formatted")

    def mcu_reset(self):
        com = Com(Command.CMD_RESET)
        com.transceive(self.serial)
        logging.info("Reset MCU done")

    def sensor_calibrate(self):
        com = Com(Command.CMD_STORAGE_CALIBRATION)
        com.transceive(self.serial)
        logging.info("Sensor calibrated and data stored in flash. Restart to activate.")

    def sensor_calibrate_remove(self):
        com = Com(Command.CMD_STORAGE_CALIBRATION, Argument.ARG_DELETE)
        com.transceive(self.serial)
        logging.info("Sensor calibration data deleted from flash. Restart to activate.")

    def sensor_properties_get(self):
        """ Get sensor properties"""
        com = Com(Command.CMD_SENSOR, Argument.ARG_PROPERTIES)
        com.transceive(self.serial)

        prop = OrderedDict()
        if Argument.ARG_SENSOR_TYPE in com.keys_rx:
            prop['sensor_type'] = BepTargetParameters.SENSOR_TYPES_BY_VALUE[
                com.get_as_uint(Argument.ARG_SENSOR_TYPE)]
        if Argument.ARG_WIDTH in com.keys_rx:
            prop['width'] = com.get_as_uint(Argument.ARG_WIDTH)
        if Argument.ARG_HEIGHT in com.keys_rx:
            prop['height'] = com.get_as_uint(Argument.ARG_HEIGHT)
        if Argument.ARG_DPI in com.keys_rx:
            prop['dpi'] = com.get_as_uint(Argument.ARG_DPI)
        if Argument.ARG_MAX_SPI_CLOCK in com.keys_rx:
            prop['max_spi_clock'] = com.get_as_uint(Argument.ARG_MAX_SPI_CLOCK)
        if Argument.ARG_NUM_SUB_AREAS_WIDTH in com.keys_rx:
            prop['num_sub_areas_width'] = com.get_as_uint(Argument.ARG_NUM_SUB_AREAS_WIDTH)
        if Argument.ARG_NUM_SUB_AREAS_HEIGHT in com.keys_rx:
            prop['num_sub_areas_height'] = com.get_as_uint(Argument.ARG_NUM_SUB_AREAS_HEIGHT)

        logging.info("Sensor properties:\n%s",
                     "\n".join("  {}: {}".format(k, p) for k, p in prop.items()))

        return prop

    def stack_fill(self):
        com = Com(Command.CMD_DEBUG, Argument.ARG_STACK)
        com.add_arg(Argument.ARG_FILL)
        com.transceive(self.serial)
        logging.info("Stack filled with predefined pattern")

    def stack_read(self):
        """Read max stack usage since stack fill"""
        com = Com(Command.CMD_DEBUG, Argument.ARG_STACK)
        com.add_arg(Argument.ARG_GET)
        com.transceive(self.serial)

        max_stack = com.get_as_uint(Argument.ARG_DATA)
        assert max_stack, "Parameter read error"
        logging.info("Max stack usage %s", max_stack)

        return max_stack

    def heap_read(self):
        """Read heap high water mark"""
        com = Com(Command.CMD_DEBUG, Argument.ARG_HEAP)
        com.transceive(self.serial)

        max_heap = com.get_as_uint(Argument.ARG_DATA)
        assert max_heap, "Parameter read error"
        logging.info("Max heap usage %s", max_heap)

        return max_heap

    def log_level_set(self, level=None):
        """Set requested log level"""
        if level is None:
            try:
                levels_info = ', '.join(
                    "{}={}".format(desc.replace("FPC_LOG_LEVEL_", ""), l) for desc, l in
                    sorted(BepTargetParameters.LOG_LEVELS.items(), key=lambda x: x[1]))
                level = int(input("Enter log level [{}] >> ".format(levels_info)))
            except ValueError:
                logging.error("Invalid log level!")
                return

        assert level in BepTargetParameters.LOG_LEVELS.values(), "Invalid log level!"

        com = Com(Command.CMD_LOG, Argument.ARG_SET)
        com.add_arg(Argument.ARG_LEVEL, level.to_bytes(1, byteorder='little'))
        com.transceive(self.serial)

        logging.info("Log level set to %i [%s].", level, BepTargetParameters.LOG_LEVELS_BY_VALUE[
            level].replace("FPC_LOG_LEVEL_", ""))

    def log_level_get(self):
        """Get current log level"""
        com = Com(Command.CMD_LOG, Argument.ARG_GET)
        com.add_arg(Argument.ARG_LEVEL)
        com.transceive(self.serial)

        level = com.get_as_uint(Argument.ARG_LEVEL)
        logging.info("Current log level: %i [%s]", level,
                     BepTargetParameters.LOG_LEVELS_BY_VALUE[level].replace("FPC_LOG_LEVEL_", ""))

        return level

    def log_mode_set(self, mode=None):
        """Set requested log mode"""
        if mode is None:
            try:
                modes_info = ', '.join(
                    "{}={}".format(desc.replace("FPC_LOG_LEVEL_", ""), m) for desc, m in
                    sorted(BepTargetParameters.LOG_MODES.items(), key=lambda x: x[1]))
                mode = int(input("Enter log mode [{}] >> ".format(modes_info)))
            except ValueError:
                logging.error("Invalid log mode!")
                return

        assert mode in BepTargetParameters.LOG_MODES.values(), "Invalid log mode!"

        com = Com(Command.CMD_LOG, Argument.ARG_SET)
        com.add_arg(Argument.ARG_MODE, mode.to_bytes(1, byteorder='little'))
        com.transceive(self.serial)

        logging.info("Log mode set to %i [%s].", mode, BepTargetParameters.LOG_MODES_BY_VALUE[
            mode].replace("FPC_LOG_MODE_", ""))

    def log_mode_get(self):
        """Get current log mode"""
        com = Com(Command.CMD_LOG, Argument.ARG_GET)
        com.add_arg(Argument.ARG_MODE)
        com.transceive(self.serial)

        mode = com.get_as_uint(Argument.ARG_MODE)
        logging.info("Current log mode: %i [%s]", mode,
                     BepTargetParameters.LOG_MODES_BY_VALUE[mode].replace("FPC_LOG_MODE_", ""))

        return mode

    def log_extract(self):
        """Extract logs"""
        logs = b''
        max_loops = 10

        while max_loops > 0:
            max_loops -= 1
            com = Com(Command.CMD_LOG, Argument.ARG_EXTRACT)
            com.transceive(self.serial)

            if Argument.ARG_DATA in com.keys_rx:
                logs += com.keys_rx[Argument.ARG_DATA]

            if Argument.ARG_FINISH in com.keys_rx:
                break

        if logs:
            logging.info("Extracted logs:\n%s", logs.decode('utf-8'))
        else:
            logging.info("Extracted logs: No logs available")

        return logs

    def version_get(self):
        """Get software version"""
        version = None

        com = Com(Command.CMD_INFO, Argument.ARG_GET)
        com.add_arg(Argument.ARG_VERSION)
        com.transceive(self.serial)

        version = com.get_as_string(Argument.ARG_VERSION)
        logging.info("Version:\n%s", version)

        return version

    def unique_id_get(self):
        """Get unquie id"""
        unique_id = b''
        unique_id_str = ''

        com = Com(Command.CMD_INFO, Argument.ARG_GET)
        com.add_arg(Argument.ARG_UNIQUE_ID)
        com.transceive(self.serial)

        unique_id = com.get_key_data(Argument.ARG_UNIQUE_ID)

        for data in unique_id:
            unique_id_str += "0x%02x " % int(data)
        logging.info("Unique id (LSB): %s\n", unique_id_str)

        return unique_id


    def uart_speed_set(self, speed=None):
        """Set requested communication speed"""
        if speed is None:
            try:
                available_speeds = self.uart_speed_get()
                speed = int(input("Enter baud rate >> "))
                if speed not in available_speeds:
                    raise ValueError
            except ValueError:
                logging.error("Invalid number!")
                return

        com = Com(Command.CMD_COMMUNICATION, Argument.ARG_SPEED)
        com.add_arg(Argument.ARG_SET)
        com.add_arg(Argument.ARG_DATA, speed.to_bytes(4, byteorder='little'))
        com.transceive(self.serial)

        # Reconfigure our own baud rate
        self.serial.baudrate = speed

        logging.info("Communication speed set to %i.", speed)

    def uart_speed_get(self):
        """Get available communication speeds"""
        com = Com(Command.CMD_COMMUNICATION, Argument.ARG_SPEED)
        com.add_arg(Argument.ARG_GET)
        com.transceive(self.serial)

        speeds = com.get_as_uint_list(Argument.ARG_DATA, '<L')
        logging.info("Available baud rates: %s", " , ".join(str(i) for i in speeds))

        return speeds


    def sensor_reset(self):
        """Reset sensor"""
        com = Com(Command.CMD_SENSOR, Argument.ARG_RESET)
        com.transceive(self.serial)
        logging.info("Sensor successfully reset")

    def sensor_prod_test(self):
        """Get Production test result"""

        com = Com(Command.CMD_SENSOR, Argument.ARG_PROD_TEST)
        com.transceive(self.serial)

        feedback = com.get_as_uint(Argument.ARG_PROD_TEST)
        if feedback != BepTargetParameters.PROD_TEST_FEEDBACK["FPC_BEP_SENSOR_TEST_OK"] :
            feedback = BepTargetParameters.PROD_TEST_FEEDBACK["FPC_BEP_SENSOR_TEST_FAILED"]

        assert feedback in BepTargetParameters.PROD_TEST_FEEDBACK.values(), \
            "Invalid production test feedback (%d)!" % feedback
        logging.info("Production test result: %i (%s)", feedback, BepTargetParameters.PROD_TEST_FEEDBACK_BY_VALUE[feedback])

        return feedback

    def sensor_wait_finger_present(self, timeout_ms=None, sleep_counter=None):
        """Wait for finger present on sensor"""
        com = Com(Command.CMD_WAIT, Argument.ARG_FINGER_DOWN)

        if timeout_ms is None:
            try:
                timeout_ms = int(input("Enter timeout in ms (0 for infinity) >> "))
            except ValueError:
                logging.error("Invalid wait time!")
                return

        if timeout_ms != 0:
            # Send timeout_ms as uint16_t, 2 bytes
            com.add_arg(Argument.ARG_TIMEOUT, timeout_ms.to_bytes(2, byteorder='little'))

        if sleep_counter is None:
            try:
                sleep_counter = int(input("Enter finger detect sleep polling interval in ms (4-1020) >> "))
            except ValueError:
                logging.error("Invalid wait time!")
                return

        if sleep_counter != 0:
            # Send sleep_counter as uint16_t, 2 bytes
            com.add_arg(Argument.ARG_SLEEP, sleep_counter.to_bytes(2, byteorder='little'))

        logging.info("Waiting for finger present (timeout = %d ms sleep polling interval = %d ms)...",
                     timeout_ms, sleep_counter)

        com.transceive(self.serial)
        logging.info("Finger present")

    def sensor_wait_finger_not_present(self, timeout_ms=None):
        """Wait for finger not present on sensor"""
        com = Com(Command.CMD_WAIT, Argument.ARG_FINGER_UP)

        if timeout_ms is None:
            try:
                timeout_ms = int(input("Enter timeout in ms (0 for infinity) >> "))
            except ValueError:
                logging.error("Invalid wait time!")
                return

        if timeout_ms != 0:
            # Send timeout_ms as uint16_t, 2 bytes
            com.add_arg(Argument.ARG_TIMEOUT, timeout_ms.to_bytes(2, byteorder='little'))

        logging.info("Waiting for finger not present (timeout = %d ms)...", timeout_ms)

        com.transceive(self.serial)
        logging.info("Finger not present")
