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

"""Comport functions"""

import sys
import logging
try:
    import serial
    import serial.tools.list_ports
except ImportError:
    sys.exit("This tool requires the pyserial Python module. Install it using:"
             "\n $ sudo apt-get install python3-serial")


# pylint: disable=too-many-ancestors
class Uart(serial.Serial):
    """Class to access comport"""

    def __init__(self):
        super().__init__()
        self.baudrate = 115200
        self.port = None

    def connect(self, port=None, speed=None, timeout=None):
        if self.port or port:
            if port:
                self.port = port

            if speed:
                self.baudrate = speed

            if timeout:
                self.timeout = timeout

            try:
                self.open()
                logging.info("UART %s opened @ %d Bd", self.port, self.baudrate)
                return True

            except serial.SerialException as error:
                logging.error("Failed to open port due to %s", error)
                return False
            return False

    def find(self, uid=None):
        """Find serial port where J-Link is connected

        If several J-Link debuggers are connected the first found
        will be selected if uid is not set"""

        comports = list(serial.tools.list_ports.comports())
        port = None

        for comport in comports:
            if 'J-Link - CDC' in comport.description:
                if not uid or uid in comport.hwid:
                    port = '/dev/' + comport.name

        if port:
            self.port = port
            logging.info("Comport %s is used", port)
            return True

        logging.error("Couldn't find comport")
        return False

    def get_port(self):
        return self.port

    def get_speed(self):
        return self.baudrate

    def set_speed(self, speed):
        self.baudrate = speed

    def flush(self):
        self.reset_output_buffer()
        self.reset_input_buffer()
