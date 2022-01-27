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

"""Raspberry Pi SPI functions"""
# pylint: skip-file
import sys
import time
import logging
import spidev
import RPi.GPIO as GPIO

HOST_IRQ_PIN = 17


class Rpispi(object):
    """Class to access Rpi SPI"""

    def __init__(self):
        self.spi = spidev.SpiDev()
        self.port = "SPI0"
        self.timeout = 0
        GPIO.setmode(GPIO.BCM)

    def connect(self, port=None, speed=None, timeout=None):
        """Connect to Rpi SPI interface"""
        # Speed must be exact rates so hardcoded here for now
        speed = 976000
        self.spi.open(0, 0)
        self.spi.max_speed_hz = speed
        self.timeout = timeout
        GPIO.setup(HOST_IRQ_PIN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        return True

    def find(self, uid=None):
        return True

    def get_port(self):
        return self.port

    def get_speed(self):
        return self.spi.max_speed_hz

    def set_speed(self, speed):
        self.spi.max_speed_hz = speed

    def close(self):
        self.spi.close()

    def flush(self):
        return True

    def write(self, data):
        # Convert byte array to list
        dlist = []
        for d in data:
            dlist.append(d)
        self.spi.xfer(dlist)

    def read(self, length):
        timestamp = time.time()
        logging.debug("Read")

        while not GPIO.input(HOST_IRQ_PIN) == 1:
            if self.timeout and timestamp + self.timeout < time.time():
                return None

        dlist = self.spi.readbytes(length)
        # Convert list to byte array
        data = bytes(dlist)

        return data
