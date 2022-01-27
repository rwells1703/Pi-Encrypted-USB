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

"""Communication interface against BEP"""

import binascii
import enum
import logging
import struct
from abc import ABCMeta

TRANSCEIVE_TRIES = 3

# Program specific commands base address
CMD_APP_BASE_VAL = 0xE000

# Program specific arguments base address
ARG_APP_BASE_VAL = 0x7000

FPC_COM_ACK = b'\x7f\xff\x01\x7f'


class CommandBase(enum.IntEnum):
    __metaclass__ = ABCMeta


class Command(CommandBase):
    # BEP commands
    """ Biometry """
    CMD_CAPTURE = 0x0001
    CMD_ENROLL = 0x0002
    CMD_IDENTIFY = 0x0003
    CMD_MATCH = 0x0004
    CMD_IMAGE = 0x0005
    CMD_TEMPLATE = 0x0006
    CMD_WAIT = 0x0007
    CMD_SETTINGS = 0x0008

    """ Sensor """
    CMD_NAVIGATE = 0x1001
    CMD_SENSOR = 0x1002
    CMD_DEADPIXELS = 0x1003

    """ Security """
    CMD_CONNECT = 0x2001
    CMD_RECONNECT = 0x2002

    """ Firmware """
    CMD_FW_UPGRADE = 0x3001
    CMD_RESET = 0x3002
    CMD_CANCEL = 0x3003
    CMD_INFO = 0x3004

    """ Storage """
    CMD_STORAGE = 0x4001
    CMD_STORAGE_TEMPLATE = 0x4002
    CMD_STORAGE_CALIBRATION = 0x4003
    CMD_STORAGE_LOG = 0x4004
    CMD_STORAGE_SETTINGS = 0x4005

    """ Hardware """
    CMD_TEST = 0x5001
    CMD_MCU = 0x5002
    CMD_GPIO = 0x5003

    """ Communication """
    CMD_COMMUNICATION = 0x6001

    """ Application specific commands """
    CMD_APP_BASE = CMD_APP_BASE_VAL

    """ Log """
    CMD_LOG = 0xF001
    CMD_DEBUG = 0xF002
    CMD_DIAG = 0xF003


class ProgramSpecificCommand(CommandBase):
    # Program Specific Commands
    """ HMOC """
    CMD_APP_HMOC = CMD_APP_BASE_VAL + 0x001


class ArgumentBase(enum.IntEnum):
    __metaclass__ = ABCMeta


class Argument(ArgumentBase):
    # Arguments to BEP commands
    """ Biometry """
    ARG_FINGER_DOWN = 0x0001
    ARG_FINGER_UP = 0x0002
    ARG_START = 0x0003
    ARG_ADD = 0x0004
    ARG_FINISH = 0x0005
    ARG_ID = 0x0006
    ARG_ALL = 0x0007
    ARG_EXTRACT = 0x0008
    ARG_MATCH_IMAGE = 0x0009
    ARG_MATCH = 0x000A

    """ Data """
    ARG_ACQUIRE = 0x1001
    ARG_RELEASE = 0x1002
    ARG_SET = 0x1003
    ARG_GET = 0x1004
    ARG_UPLOAD = 0x1005
    ARG_DOWNLOAD = 0x1006
    ARG_CREATE = 0x1007
    ARG_SAVE = 0x1008
    ARG_DELETE = 0x1009
    ARG_DATA = 0x100A
    ARG_UPDATE = 0x100B
    ARG_SEQ_NR = 0x100C
    ARG_SEQ_LEN = 0x100D

    """ Results """
    ARG_RESULT = 0x2001
    ARG_COUNT = 0x2002
    ARG_SIZE = 0x2003
    ARG_LEVEL = 0x2004
    ARG_FORMAT = 0x2005
    ARG_FLAG = 0x2006
    ARG_PROPERTIES = 0x2007
    ARG_SPEED = 0x2008
    ARG_PROD_TEST = 0x2009

    """ Sensor """
    ARG_SENSOR_TYPE = 0x3001
    ARG_WIDTH = 0x3002
    ARG_HEIGHT = 0x3003
    ARG_RESET = 0x3004
    ARG_DPI = 0x3005
    ARG_MAX_SPI_CLOCK = 0x3006
    ARG_NUM_SUB_AREAS_WIDTH = 0x3007
    ARG_NUM_SUB_AREAS_HEIGHT = 0x3008

    """ MCU """
    ARG_IDLE = 0x4001
    ARG_SLEEP = 0x4002
    ARG_DEEP_SLEEP = 0x4003
    ARG_POWER_MODE = 0x4004
    ARG_BUSY_WAIT = 0x4005

    """ Misc """
    ARG_TIMEOUT = 0x5001
    ARG_DONE = 0x5002

    """ Info """
    ARG_BOOT = 0x6001
    ARG_STATUS = 0x6002
    ARG_VERSION = 0x6003
    ARG_UNIQUE_ID = 0x6004

    """ Application specific arguments """
    ARG_APP_BASE = ARG_APP_BASE_VAL

    """ VSM """
    ARG_NONCE = 0x8001
    ARG_MAC = 0x8002
    ARG_RANDOM = 0x8003
    ARG_CLAIM = 0x8004
    ARG_PUBLIC_KEY = 0x8005
    ARG_CIPHERTEXT = 0x8006

    """ Communication """
    ARG_MTU = 0x9001

    """ Debug """
    ARG_STACK = 0xE001
    ARG_FILL = 0xE002
    ARG_HEAP = 0xE003

    """ Log """
    ARG_MODE = 0xF001
    ARG_DEBUG = 0xF002


class ProgramSpecificArgument(ArgumentBase):
    # Program Specific Arguments to BEP commands
    """ Configuration keys """
    ARG_GENERAL_TEMPLATE_SIZE = ARG_APP_BASE_VAL + 0x001
    ARG_GENERAL_LATENCY_SCHEME = ARG_APP_BASE_VAL + 0x002
    ARG_PREPROC = ARG_APP_BASE_VAL + 0x003
    ARG_ENROLL_MIN_IMAGE_QUALITY = ARG_APP_BASE_VAL + 0x004
    ARG_ENROLL_MIN_SENSOR_COVERAGE = ARG_APP_BASE_VAL + 0x005
    ARG_ENROLL_NBR_OF_IMAGES = ARG_APP_BASE_VAL + 0x006
    ARG_IDENTIFY_TEMPLATE_UPDATE = ARG_APP_BASE_VAL + 0x007
    ARG_IDENTIFY_SECURITY_LEVEL = ARG_APP_BASE_VAL + 0x008
    ARG_HMOC_LIB_MAGIC = ARG_APP_BASE_VAL + 0x009
    ARG_FINGER_DETECT_ZONES = ARG_APP_BASE_VAL + 0x00A
    ARG_CMN = ARG_APP_BASE_VAL + 0x00B
    ARG_ALGORITHM = ARG_APP_BASE_VAL + 0x00C
    ARG_SET_CAPTURE_RESOLUTION = ARG_APP_BASE_VAL + 0x00D
    ARG_SUBTEMPLATE_SAVE = ARG_APP_BASE_VAL + 0x00E
    ARG_SUBTEMPLATE_LOAD = ARG_APP_BASE_VAL + 0x00F
    ARG_DRIVER_MECHANISM = ARG_APP_BASE_VAL + 0x010
    ARG_RESET_TYPE = ARG_APP_BASE_VAL + 0x011
    """ HMOC arguments """
    ARG_HMOC_FINGER_CODE = ARG_APP_BASE_VAL + 0x100
    ARG_HMOC_CONFIG_CONTAINER = ARG_APP_BASE_VAL + 0x101
    ARG_HMOC_NUM_CONTAINERS = ARG_APP_BASE_VAL + 0x102
    ARG_HMOC_RFU = ARG_APP_BASE_VAL + 0x103
    ARG_HMOC_MAX_TEMPLATE_SIZE = ARG_APP_BASE_VAL + 0x104
    """ Matcher arguments """
    ARG_IDENTIFY_FSAL = ARG_APP_BASE_VAL + 0x200


BEP_RESULT = {
    0: "No errors occurred",
    -1: "General error",
    -2: "Internal error",
    -3: "Invalid argument",
    -4: "The functionality is not implemented",
    -5: "The operation was cancelled",
    -6: "Out of memory",
    -7: "Resources are not available",
    -8: "An I/O error occurred",
    -9: "Sensor is broken",
    -10: "The operation cannot be performed in the current state",
    -11: "The operation timed out",
    -12: "The ID is not unique",
    -13: "The ID is not found",
    -14: "The format is invalid",
    -15: "An image capture error occurred",
    -16: "Sensor hardware id mismatch",
    -17: "Invalid parameter",
    -18: "No template found",
    -19: "Invalid calibration",
    -20: "Calibration/template storage not formatted",
    -21: "Sensor hasn't been initialized",
    -22: "Too many bad images for enroll",
    -23: "Cryptographic operation failed",
    -24: "Functionality is not supported",
    -25: "Finger not stable during image capture",
    -26: "The functionality could not be used before it's initialized"
}

COM_RESULT = {
    0: "No errors occurred",
    1: "Out of memory",
    2: "Invalid argument",
    3: "The functionality is not implemented",
    4: "An I/O error occurred",
    5: "A timeout occurred",
}


class Com(object):
    """Communication interface against BEP"""

    def __init__(self, cmd, argument=None, mtu=256):
        self.args = b''
        self.args_nr = 0
        self.keys_rx = {}
        self.cmd = None
        self.mtu = mtu

        self.set_cmd(cmd)
        if argument is not None:
            self.add_arg(argument)

    def set_cmd(self, cmd):
        assert issubclass(cmd.__class__, CommandBase), "Invalid command %s" % cmd
        self.cmd = cmd

    def add_arg(self, argument, payload=None):
        assert issubclass(argument.__class__, ArgumentBase), "Invalid argument %s" % argument
        size = 0

        if payload is not None:
            size = len(payload)

        self.args += struct.pack('HH', argument, size)

        if payload is not None:
            self.args += payload

        self.args_nr += 1

    def _tx_application(self, serial):
        offset_start = 0
        offset_end = 0
        seq_nr = 1
        status = True

        # Serialize the application packet
        application_packet = struct.pack('<HH', self.cmd, self.args_nr)
        if self.args_nr:
            application_packet += self.args

        # Calc total packet size
        data_left = len(application_packet)

        # Application MTU size is PHY MTU - (Transport and Link overhead)
        app_mtu = self.mtu - self._transport_overhead() - self._link_overhead()

        # Calculate sequence length
        seq_len = (data_left // app_mtu) + 1

        while data_left > 0 and status is True:
            if data_left < app_mtu:
                offset_end += data_left
            else:
                offset_end += app_mtu

            app_data = application_packet[offset_start:offset_end]
            status = self._tx_transport(serial, seq_nr, seq_len, app_data)

            data_left -= (offset_end - offset_start)
            offset_start = offset_end
            seq_nr += 1

        return status

    def _tx_transport(self, serial, seq_nr, seq_len, app_data):
        transport_data = struct.pack('<HHH', len(app_data), seq_nr, seq_len) + app_data
        return self._tx_link(serial, transport_data)

    @staticmethod
    def _tx_link(serial, transport_data):
        channel = 1

        crc = struct.pack('<L', binascii.crc32(transport_data))
        link_data = struct.pack('<HH', channel, len(transport_data)) + transport_data + crc

        serial.write(link_data)

        # Print sent data to log
        sent = ''
        for byte in link_data[:min(len(link_data), 32)]:
            sent += "0x%02x " % int(byte)
        logging.debug("TX: Sent %s bytes", len(link_data))
        logging.debug("TX: Sent data: %s", sent)

        # Wait for ACK
        ack = bytes(serial.read(4))

        return ack == FPC_COM_ACK

    @staticmethod
    def _transport_overhead():
        overhead = 2   # Size
        overhead += 2  # Sequence length
        overhead += 2  # Sequence number
        return overhead

    @staticmethod
    def _link_overhead():
        overhead = 2   # Channel
        overhead += 2  # Size
        overhead += 4  # CRC
        return overhead

    def _rx_application(self, serial):

        status, application_package = self._rx_transport(serial)

        if status:
            cmd = struct.unpack('<H', application_package[:2])[0]

            if cmd != self.cmd:
                logging.error("Command mismatch. Sent %s, received %s", self.cmd, Command(cmd))
                return False
            args_nr = struct.unpack('<H', application_package[2:4])[0]
            self._extract_args(application_package[4:], args_nr)

        return status

    def _rx_transport(self, serial):
        status = True
        seq_nr = 0
        seq_len = 1
        application_package = b''

        while seq_nr < seq_len and status is True:
            (status, transport_package) = self._rx_link(serial)

            if status is True:
                seq_nr = struct.unpack('<H', transport_package[2:4])[0]
                seq_len = struct.unpack('<H', transport_package[4:6])[0]
                application_package += transport_package[6:]
                if seq_len > 1:
                    logging.info("Seqence %s of %s", seq_nr, seq_len)

        return status, application_package

    def _rx_link(self, serial):
        # Get size, msg and CRC
        link_header = serial.read(4)

        if not link_header:
            logging.error("Timed out waiting for response.")
            return False, []

        # channel = struct.unpack('<H', link_header[:2])[0]
        size = struct.unpack('<H', link_header[2:4])[0]
        assert size, "Received a response without size"

        # Check if size plus header and crc is larger than max package size.
        if self.mtu < size + 8:
            logging.error("Invalid size %d, larger than MTU %d.", size, self.mtu)
            return False, []

        data = serial.read(size + 4)
        link_data = data[:-4]
        crc = struct.unpack('<L', data[-4:])[0]

        crc_calc = binascii.crc32(link_data)

        if crc_calc != crc:
            logging.error("CRC mismatch. Calculated %s, received %s", crc_calc, crc)
            return False, []

        # Send Ack
        serial.write(FPC_COM_ACK)

        # Print received data to log
        received = ''
        for byte in link_header[1:3] + link_data[:min(len(link_data), 32)]:
            received += "0x%02x " % int(byte)
        logging.debug("RX: Received %s bytes", len(link_header[2:4] + link_data))
        logging.debug("RX: Received data: %s", received)

        return True, link_data

    def _extract_args(self, args, args_nr):
        for _ in range(args_nr):
            (key, size) = struct.unpack('<HH', args[:4])

            data = args[4: size + 4]
            if data and len(data) < 10:
                key_data = ''
                for byte in data:
                    key_data += "0x%02x " % int(byte)
                logging.debug("RX: Got key 0x%04x with %s byte of data: %s", key, size, key_data)
            else:
                logging.debug("RX: Got key 0x%04x with %s byte of data", key, size)

            self.keys_rx[key] = data
            args = args[size + 4:]

    def transceive(self, serial):
        """Transmit and receive data"""
        status = self.transmit(serial)
        if status is True:
            self.receive(serial)
        else:
            logging.error("No ACK received")
        self.check_result()

    def transmit(self, serial):
        """Transmit data"""
        serial.flush()

        # Send Packet
        return self._tx_application(serial)

    def receive(self, serial):
        """Receive data"""
        return self._rx_application(serial)

    @staticmethod
    def result_to_string(result):
        assert result in BEP_RESULT, "Unknown result code"
        return BEP_RESULT[result]

    def get_result(self):
        assert Argument.ARG_RESULT in self.keys_rx, "Result not received"
        return struct.unpack('b', self.keys_rx[Argument.ARG_RESULT])[0]

    def check_result(self):
        result = self.get_result()
        assert result == 0, 'Failure. Result code %d, "%s"' % \
                            (result, self.result_to_string(result))

    def get_key_data(self, key):
        assert key in self.keys_rx, "Argument %s is missing in the response" % key
        return self.keys_rx[key]

    def get_as_uint(self, key):
        assert key in self.keys_rx, "Argument %s is missing in the response" % key

        format_type = ''
        if len(self.keys_rx[key]) == 1:
            format_type = '<B'
        elif len(self.keys_rx[key]) == 2:
            format_type = '<H'
        elif len(self.keys_rx[key]) == 4:
            format_type = '<L'
        elif len(self.keys_rx[key]) == 8:
            format_type = '<Q'
        else:
            assert "Invalid size for number"

        # Always return tuple, so remove second value
        return struct.unpack(format_type, self.keys_rx[key])[0]

    def get_as_uint_list(self, key, fmt):
        assert key in self.keys_rx, "Argument %s is missing in the response" % key

        return [i[0] for i in struct.iter_unpack(fmt, self.keys_rx[key])]

    def get_as_string(self, key):
        assert key in self.keys_rx, "Argument %s is missing in the response" % key

        count = len(self.keys_rx[key])
        if not count:
            return ""

        # Always return tuple, so remove second value
        return struct.unpack('<%ds' % count, self.keys_rx[key])[0].decode('utf-8')
