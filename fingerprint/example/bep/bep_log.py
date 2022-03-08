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

"""This module will collect KPI data from BEP via the GDB server"""

import csv
import logging
import telnetlib
import threading

import serial
import numpy  # pylint: disable=import-error


class BepLoggingError(Exception):
    pass


class BepLogging(threading.Thread):
    """This class will collect data from BEP/GDB server"""
    def __init__(self, port, speed=115200, kpi_file=None):
        super(BepLogging, self).__init__()
        self._stop_event = threading.Event()
        self.samples = dict()
        self.kpi_file = kpi_file
        self.example_test_passed = None
        self.log_interface = None
        self.log_interface_type = None

        self._interface_init(port, speed)

    def _interface_init(self, port, speed):
        if 'USB' in port:
            try:
                uart = serial.Serial()
                uart.baudrate = speed
                uart.port = port
                uart.open()
                uart.flushInput()
                uart.timeout = 1
                self.log_interface = uart
                self.log_interface_type = 'uart'
                logging.info("Comport %s opened for logging", uart.port)
            except serial.SerialException as error:
                assert False, "Failed to open port due to %s" % error
        else:
            try:
                self.log_interface = telnetlib.Telnet('localhost', port)
                self.log_interface_type = 'telnet'
                logging.info("Collecting logs from ITM output")
            except ConnectionRefusedError:
                raise BepLoggingError("Couldn't connect to the GDB server")

    def stop(self):
        self._stop_event.set()
        self.join()

    def run(self):
        while True:
            if self._stop_event.is_set():
                self.log_interface.close()
                return

            try:
                if self.log_interface_type == 'telnet':
                    data = self.log_interface.read_until(b'\n', timeout=1).decode().strip()
                else:
                    data = self.log_interface.readline().decode().strip()
                if data:
                    self._handle_data(data)
            except EOFError:
                return
            except UnicodeDecodeError as error:
                logging.error(error)

    def _handle_data(self, data):
        try:
            if 'I' in data.split(' ', 7):
                data = ''.join(data.split(':')[1:])[1:]
                logging.info(data)
            elif 'D' in data.split(' ', 7):
                data = ''.join(data.split(':')[1:])[1:]
                logging.debug(data)
            elif 'E' in data.split(' ', 7):
                data = ''.join(data.split(':')[1:])[1:]
                logging.error(data)
        except IndexError as error:
            logging.error(error)
            logging.error(data)

        if ': ticks=' in data:
            self._add_kpi_data(data)
            if self.log_interface_type != 'uart':
                logging.info(data)
        elif 'PASS' in data:
            self.example_test_passed = True
        elif 'FAIL' in data:
            self.example_test_passed = False

    def get_example_test_pass(self):
        temp = self.example_test_passed
        self.example_test_passed = None
        return temp

    def _add_kpi_data(self, data):
        # Extract data from ITM
        try:
            if self.log_interface_type == 'telnet':
                name = data.split(':')[0]
            else:
                name = data.split(' ')[0]
            value = int(data.split('=')[1])
        except ValueError as error:
            logging.error(error)
            logging.error(data)
            return
        except IndexError as error:
            logging.error(error)
            logging.error(data)
            return

        # Store data in csv/excel file
        if self.kpi_file:
            with open(self.kpi_file, 'a', newline='') as csvfile:
                csv_writer = csv.writer(csvfile, quoting=csv.QUOTE_MINIMAL, skipinitialspace=True)
                csv_writer.writerow([name, value])

        self.kpi_add(name, value)

    def kpi_add(self, name, value):
        # Store data in local dictionary
        if name not in self.samples:
            self.samples[name] = []
        self.samples[name].append(value)

    def kpi_key_rename(self, old, new):
        if new in self.samples:
            self.samples[new] += self.samples[old]
            logging.debug("KPI log post already exist. Appending samples instead")
        else:
            self.samples[new] = self.samples[old]
        del self.samples[old]

    def kpi_count(self, name):
        if name in self.samples:
            return len(self.samples[name])
        return 0

    def kpi_value_remove_last(self, name):
        if name in self.samples:
            return self.samples[name].pop()
        return None

    def kpi_values_log(self):
        logging.info("\n{:<38}{:<6}{:<6}{:<8}{:<6}{:<6}"
                     .format('KPI', 'Max', 'Mean', 'Median', 'Min', 'Samples'))
        logging.info('-' * 72)
        for (key, value) in sorted(self.samples.items()):
            logging.info("{:<38}{:<6d}{:<6.0f}{:<8.0f}{:<6d}{:<6}"
                         .format(key, max(value), numpy.mean(value), numpy.median(value),
                                 min(value), len(value)))
        log_msg = '-' * 72 + '\n'
        logging.info(log_msg)

    def kpi_values_get(self):
        return self.samples

    def kpi_values_flush(self):
        self.samples = dict()
