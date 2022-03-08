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

"""BEP utility functions"""

import sys
import math
import logging
try:
    from PIL import Image
except ImportError:
    sys.exit("This tool requires the Python PIL module. Install it using:"
             "\n $ sudo apt-get install python3-pil")


def read_file(file_name, mode='rb'):
    """Opens and reads data from the specified file"""
    data = None
    try:
        with open(file_name, mode) as file:
            data = file.read()
            logging.debug("Read file: %s (%d bytes)", file_name, len(data))
    except IOError as error:
        assert False, "Failed read from file '%s' (%s)" % (file_name, error)
    return data


def write_file(data, file_name, mode='wb'):
    """ Writes data to file """
    try:
        with open(file_name, mode) as file:
            file.write(data)
            logging.debug("Wrote file: %s (%d bytes)", file_name, len(data))
    except IOError as error:
        assert False, "Failed write to file, %s (%s) " % (file_name, error)


def convert_image(raw_image, display=True, filename_out='image.png', width=0, height=0):
    """
    Convert and display/save a raw image from BEP

    The function only supports raw image data extracted from BEP. This means
    image data with 8-bit greyscale format.

    :param raw_image: Raw image pixel data buffer.
    :param display: Enables display of image.
    :param filename_out:  Output image file name, the extension determines the image format.
    :param width: Raw image width, if not set square image is assumed.
    :param height: Raw image height, if not set square image is assumed.
    """
    size = len(raw_image)
    if width == 0 or height == 0:
        width = int(math.sqrt(size))
        height = width

    img = Image.frombytes('L', (width, height), raw_image, 'raw')

    if display:
        img.show()
    if filename_out:
        print("Image saved as", filename_out)
        img.save(filename_out)


def setup_logging(console=True, debug=False, info_file=None, debug_file=None, overwrite=False):
    """
    Setup logging.

    Logging control for log output to the console and files at different log levels.

    :param console: Enables logging to the console.
    :param debug: Enable debug prints to the console if console logging is enabled.
    :param info_file: Filename to store up to INFO level log prints.
    :param debug_file: Filename to store up to DEBUG level log prints.
    :param overwrite: Controls if log file should be truncated or not.
    """
    info_hand = None
    debug_hand = None

    log = logging.getLogger()
    log.setLevel(logging.DEBUG)

    if console:
        console_hand = logging.StreamHandler()
        if debug:
            console_hand.setLevel(logging.DEBUG)
        else:
            console_hand.setLevel(logging.INFO)
        console_hand.setFormatter(logging.Formatter('%(message)s'))
        log.addHandler(console_hand)

    if info_file is not None:
        if overwrite:
            info_hand = logging.FileHandler(info_file, mode='w')
        else:
            info_hand = logging.FileHandler(info_file)
        info_hand.setLevel(logging.INFO)
        info_hand.setFormatter(logging.Formatter('%(message)s'))
        log.addHandler(info_hand)

    if debug_file is not None:
        if overwrite:
            debug_hand = logging.FileHandler(debug_file, mode='w')
        else:
            debug_hand = logging.FileHandler(debug_file)
        debug_hand.setLevel(logging.DEBUG)
        debug_hand.setFormatter(logging.Formatter('%(filename)-20s: %(levelname)-8s: %(message)s'))
        log.addHandler(debug_hand)

    def finalizer():
        log.removeHandler(info_hand)
        log.removeHandler(debug_hand)

    return finalizer
