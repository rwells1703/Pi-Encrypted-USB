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

"""FPC5832 USB/SPI converter functions"""

import sys
import time
import logging
import os
try:
    from pyftdi.spi import SpiController, SpiIOError
    from pyftdi.usbtools import UsbToolsError
    import serial.tools.list_ports as list_ports
except ImportError:
    sys.exit("This tool requires the pyftdi Python module. Install it using:"
             "\n $ pip3 install pyftdi")


HOST_IRQ_MASK = 0x2000
HOST_RST_MASK = 0x4000

LED_GRN_MASK = 0x0100
LED_RED_MASK = 0x0200
LED_YLW_MASK = 0x0400
LED_ALL_MASK = LED_GRN_MASK | LED_RED_MASK | LED_YLW_MASK


class Fpc5832spi(object):
    """Class to access FPC5832"""

    def __init__(self):
        self.spi = SpiController(cs_count=1)
        self.port = None
        self.url = None
        self.slave = None
        self.gpio = None
        self.timeout = 0
        self.configured = False

    def __url_from_port(self, port=None):
        if port:
            desc = list(list_ports.grep(port))[0]
            if ('FPC TSD TX' in desc.description or 'FPCSSD' in desc.description or
                    'Single RS232-HS' in desc.description):
                if os.name == 'nt' or desc.serial_number is None:
                    self.url = 'ftdi://ftdi:232h/1'
                else:
                    self.url = 'ftdi://ftdi:232h:%s/1' % str(desc.serial_number)
                self.port = port

    def connect(self, port=None, speed=None, timeout=None):
        """Connect to FPC5832 using pyftdi"""
        if not self.port and port:
            self.__url_from_port(port)

        if not speed:
            speed = 1000000

        if self.url:
            try:
                logging.info("SPI connect %s", self.url)
                self.spi.configure(self.url)
                self.timeout = timeout
                self.slave = self.spi.get_port(cs=0, freq=int(speed), mode=0)
                self.gpio = self.spi.get_gpio()
                self.gpio.set_direction(LED_ALL_MASK | HOST_IRQ_MASK | HOST_RST_MASK, LED_ALL_MASK |
                                        HOST_RST_MASK)
                self.gpio.write(LED_GRN_MASK)
                logging.info("SPI port %s opened @ %d Hz", self.url, self.slave.frequency)
                return True

            except SpiIOError as error:
                logging.error("Failed to open port due to %s", error)
                return False

            except UsbToolsError as error:
                logging.error("Could not find port, error: %s", error)
                return False

        logging.error("Could not find port")
        return False

    def find(self, uid=None):
        """Find serial port where FPC5832 is connected

        If several FPC5832 are connected the first found
        will be selected if uid is not set"""

        comports = list(list_ports.comports())
        url = None
        port = None
        sernum = None

        for comport in comports:
            if ('USB Serial Port' in comport.description or 'FPC TSD TX' in comport.description or
                    'Single RS232-HS' in comport.description):
                if not uid or uid in comport.hwid:
                    if os.name == 'nt' or comport.serial_number is None:
                        url = 'ftdi://ftdi:232h/1'
                    else:
                        sernum = str(comport.serial_number)
                        url = 'ftdi://ftdi:232h:%s/1' % sernum
                    port = comport.device

        if url:
            self.url = url
            self.port = port
            logging.info("Port %s is used, URL: %s, sernum: %s, os: %s", port, url, sernum,
                         os.name)
            return True

        logging.error("Failed to find port")
        return False

    def get_port(self):
        return self.port

    def get_speed(self):
        if self.slave:
            return self.slave.frequency
        return 0

    def set_speed(self, speed):
        if self.slave:
            self.slave.set_frequency(speed)

    def close(self):
        if self.slave:
            self.spi.terminate()

    def flush(self):
        if self.slave:
            self.slave.flush()

    def write(self, data):
        if self.slave:
            self.gpio.write(LED_GRN_MASK | LED_YLW_MASK)
            self.slave.write(data)
            self.gpio.write(LED_GRN_MASK)

    def read(self, length):
        if self.slave:
            timestamp = time.time()

            self.gpio.write(LED_GRN_MASK | LED_RED_MASK)
            while not self.gpio.read() & HOST_IRQ_MASK:
                if self.timeout and timestamp + self.timeout < time.time():
                    self.gpio.write(LED_GRN_MASK)
                    return None

            self.gpio.write(LED_GRN_MASK | LED_YLW_MASK)

            data = self.slave.read(length)

            self.gpio.write(LED_GRN_MASK)

            return data
        return None
