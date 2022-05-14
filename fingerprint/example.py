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

"""This module is used to communicate with BEP"""

import argparse
import logging
import os

from fingerprint.bep import util
from fingerprint.bep.bep_extended import BepExtended
from fingerprint.bep.bep_log import BepLogging, BepLoggingError
from fingerprint.bep.com_phy import ComPhy

import encryption

def get_args():
    """Parses args from terminal"""

    parser = argparse.ArgumentParser(
        description='Host interface for communication with BEP')
    parser.add_argument(
        '-i',
        '--interface',
        help='Interface type (rpispi)',
        default='rpispi',
        required=False)
    parser.add_argument(
        '-p',
        '--port',
        help='Input port name (COMX, /dev/ttyACMX)',
        default=None,
        required=False)
    parser.add_argument(
        '-s',
        '--speed',
        help='Input communication speed',
        type=int,
        default=115200,
        required=False)
    parser.add_argument(
        '-t',
        '--timeout',
        help='Timeout for UART receive in seconds (>=2)',
        type=int,
        default=6,
        required=False)
    parser.add_argument(
        '--id',
        help="Partial or full Jlink device id",
        default=None,
        required=False)
    parser.add_argument(
        '--debug',
        help="Print debug information",
        action='store_true',
        default=False)
    parser.add_argument(
        '--log',
        help="Collect KPI data and target logs. Port number must be entered --log=[PORT]")
    parser.add_argument(
        '--gui',
        help="Start graphical user interface",
        action='store_true',
        default=False)

    return parser.parse_args()


def print_menu(menu_options, bep_interface):
    """Print menu to console"""
    while True:
        print("")
        print("----------------------")
        print()
        print("Possible options:")

        for (key, value) in sorted(menu_options.items()):
            print("%s: %s" % (key, value[1]))
        print()

        choice = input("Option>> ")
        choice.lower()
        print()

        if choice in menu_options:
            if isinstance(menu_options[choice][0], str):
                try:
                    getattr(bep_interface, menu_options[choice][0])()
                except AssertionError as error:
                    logging.error(error)
            else:
                return
        else:
            print("Option not implemented. Try again!")

        input("Press enter to continue")


def system_sub_menu(bep_interface):
    """BEP console sub-menu for system related functions"""
    menu_options = {
        '1': ['mcu_reset', "Reset MCU"],
        '2': ['stack_fill', "Fill stack"],
        '3': ['stack_read', "Read stack max usage"],
        '4': ['heap_read', "Read heap max usage"],
        '5': ['log_level_set', "Set log level"],
        '6': ['log_level_get', "Get log level"],
        '7': ['log_mode_set', "Set log mode"],
        '8': ['log_mode_get', "Get log mode"],
        '9': ['log_extract', "Extract logs"],
        'a': ['version_get', "Get software version"],
        'b': ['storage_format', "Format flash storage"],
        'c': ['unique_id_get', "Get unique ID"],
        'd': ['uart_speed_get', "Get UART speeds supported"],
        'e': ['uart_speed_set', "Set UART speed"],
        'q': [None, 'Return to main menu']
    }

    print_menu(menu_options, bep_interface)


def sensor_sub_menu(bep_interface):
    """BEP console sub-menu for sensor related functions"""
    menu_options = {
        '1': ['sensor_calibrate', "Calibrate sensor and store in flash"],
        '2': ['sensor_calibrate_remove', "Remove sensor calibration from flash"],
        '3': ['sensor_wait_finger_present', "Wait for finger present"],
        '4': ['sensor_wait_finger_not_present', "Wait for finger not present"],
        '5': ['sensor_properties_get', "Print sensor properties"],
        '6': ['sensor_prod_test', "Production test result get"],
        'q': [None, 'Return to main menu']
    }

    print_menu(menu_options, bep_interface)


def template_storage_sub_menu(bep_interface):
    """BEP console sub-menu for template storage functions"""
    menu_options = {
        '1': ['template_save', "Save template to flash"],
        '2': ['template_save_and_release', "Save template to flash and remove from RAM"],
        '3': ['template_remove_ram', "Remove template from RAM"],
        '4': ['template_remove_flash', "Remove template from flash"],
        '5': ['template_remove_all_flash', "Remove all templates from flash"],
        '6': ['template_load_from_flash', "Load template from flash storage to RAM"],
        '7': ['template_get_count', "Get number of templates in storage"],
        '8': ['template_get_ids', "Get a list of the template ids in storage"],
        'q': [None, 'Return to main menu']
    }

    print_menu(menu_options, bep_interface)


def basic_commands_menu(bep_interface):
    """BEP console sub-menu for basic functions that are not shown in main menu"""
    menu_options = {
        '1': ['capture', "Capture image"],
        '2': ['capture_timeout', "Capture image with timeout"],
        '3': ['enroll_start', "Enroll start"],
        '4': ['enroll', "Enroll"],
        '5': ['enroll_finish', "Enroll finish"],
        '6': ['image_extract', "Extract template from image"],
        '7': ['identify', "Identify by template"],
        '8': ['capture_and_enroll', "Capture and enroll"],
        '9': ['image_get', "Upload image"],
        'q': [None, 'Return to main menu']
    }

    print_menu(menu_options, bep_interface)


def menu(bep_interface, clear_cmd, timeout):
    """BEP console menu"""
    # pylint: disable=R0912

    menu_options = {
        'a': ['enroll_finger', "Enroll finger"],
        'b': ['capture_and_identify', "Capture and identify by template"],
        'c': ['template_remove_all_flash', "Remove all templates from flash"],
        'd': ['template_save_and_release', "Save template to flash and remove from RAM"],
        'e': ['template_remove_flash', "Remove template from flash"],
        'f': ['template_storage_sub_menu', "Template storage sub-menu"],
        'g': ['system_sub_menu', "System sub-menu"],
        'h': ['sensor_sub_menu', "Sensor sub-menu"],
        'i': ['basic_commands_menu', "Basic commands sub-menu"],
        'q': [None, 'Exit']
    }

    while True:
        os.system(clear_cmd)

        print("BEP host interface")
        print("Com port: %s [speed: %s]" % (bep_interface.serial.get_port(),
                                            bep_interface.serial.get_speed()))
        print("Timeout: %s s" % timeout)
        print("----------------------")
        print()
        print("Possible options:")

        for (key, value) in sorted(menu_options.items()):
            print("%s: %s" % (key, value[1]))
        print()

        choice = input("Option>> ")
        choice.lower()
        print()

        if choice in menu_options:
            if isinstance(menu_options[choice][0], str):
                if menu_options[choice][0] == "template_storage_sub_menu":
                    template_storage_sub_menu(bep_interface)
                    continue
                elif menu_options[choice][0] == "system_sub_menu":
                    system_sub_menu(bep_interface)
                    continue
                elif menu_options[choice][0] == "sensor_sub_menu":
                    sensor_sub_menu(bep_interface)
                    continue
                elif menu_options[choice][0] == "basic_commands_menu":
                    basic_commands_menu(bep_interface)
                    continue
                else:
                    try:
                        getattr(bep_interface, menu_options[choice][0])()
                    except AssertionError as error:
                        logging.error(error)
            else:
                return
        else:
            print("Option not implemented. Try again!")

        input("Press enter to continue")


def main():
    tpm = encryption.TPM()
    tpm.restart()

    """Starts a console against BEP"""
    args = get_args()
    if args.timeout < 2:
        print("Timeout argument must be >= 2")
        exit(1)
    util.setup_logging(True, args.debug, 'bep_test_info.log', 'bep_test_debug.log', True)

    if os.name == 'nt':
        clear_cmd = 'cls'
    else:
        clear_cmd = 'clear'

    phy = ComPhy(args.interface)

    if not args.port:
        assert phy.find(args.id)

    assert phy.connect(port=args.port, speed=args.speed, timeout=args.timeout)

    if args.log:
        try:
            log = BepLogging(args.log, 'kpi_log.csv')
            log.start()
        except BepLoggingError as error:
            print(error)
            exit(1)

    if not args.gui:
        bep_interface = BepExtended(phy)
        menu(bep_interface, clear_cmd, args.timeout)

    phy.close()

    if args.log:
        log.stop()
        log.join()
        log.kpi_values_log()


if __name__ == "__main__":
    main()