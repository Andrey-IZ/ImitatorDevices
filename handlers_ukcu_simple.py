#!/usr/bin/env python

import struct
import re
UKCU_SET_SIGNALS, UKCU_GET_SIGNALS, UKCU_SET_DIRECTION = 'SetSignals', 'GetSignals', 'SetDirection'

UKCU_COMMANDS = {UKCU_SET_DIRECTION: 0x01B, UKCU_SET_SIGNALS: 0x11B, UKCU_GET_SIGNALS: 0x21B}
UKCU_READ_LOW_ADDRESS, UKCU_READ_HIGH_ADDRESS = 0x1000004, 0x1000006


class UkcuPacket(object):
    def __init__(self, code=0, data=0):
        self.__code, self.__data = code, data
        self.__prefix, self.__suffix = 0xA5, 0x17
        self.__structure_packet = 'cHcIcc'
        self.__size = 4
        self.__crc_count = 8

    @property
    def data(self):
        return self.__data

    @property
    def code(self):
        return self.__code

    def parse(self, packet_bytes):
        code = struct.unpack('!H', packet_bytes[1:3])[0]
        data = struct.unpack('!I', packet_bytes[4:8])[0]
        prefix, size, crc, suffix = packet_bytes[0], packet_bytes[3], packet_bytes[8], packet_bytes[9]
        test_crc = 0
        for byte in packet_bytes[1:self.__crc_count]:
            test_crc ^= byte

        if prefix != self.__prefix or size != self.__size or \
                        crc != test_crc or suffix != self.__suffix:
            return None

        self.__code, self.__data = code, data
        return len(packet_bytes)

    def to_bytes(self):
        """
        :rtype: bytes
        :return:
        """
        array = bytearray()
        array.extend(bytes([self.__prefix]))
        array.extend(struct.pack('!H', self.__code))
        array.extend(bytes([self.__size]))
        array.extend(struct.pack('!I', self.__data))

        crc = 0
        for item_byte in array[1:]:
            crc ^= item_byte

        array.extend(bytes([crc]))
        array.extend(bytes([self.__suffix]))

        return bytes(array)


def __send_command(code, data, expected_data=0, timeout=0):
    """

    :param expected_data:
    :param timeout:
    :param data:
    :param code:
    :rtype: tuple
    """
    packet = UkcuPacket(code, data)
    return packet.to_bytes(), timeout, code, expected_data


def handler_ukcu_response(request_data, response_data=None):
    """
    Operates packet commands from serial port device to PC
    :param response_data:
    :param request_data: It is tuple. First item is bytes sending to serial device. Second item is timeout in ms for delay
    response. The rest is user arguments
    :param derived_bytes: array of bytes, which derived from PC to serial device and match with protocol record
    :return:  array's bytes to will send to PC again
    """
    packet = UkcuPacket()
    derived_bytes = request_data[0]
    code = request_data[2]
    expected_data = request_data[3]

    if not packet.parse(derived_bytes):
        raise ValueError("Invalid packet data is derived here")

    packet = UkcuPacket(code | 4, expected_data)
    return packet.to_bytes()


def handler_parser_ucku(log, bytes_recv):
    packet = UkcuPacket()
    if packet.parse(bytes_recv):
        return packet.code, packet.data
    return None


def __str_hex2byte(request):
    if not isinstance(request, str):
        return None

    str_packet_pure = re.sub(r'[^A-Za-z0-9]', '', request)
    try:
        bytes_req = bytes.fromhex(str_packet_pure)
    except ValueError as e:
        raise ValueError(
            "Error convert string to bytes: before={}; after={}; {}".format(request, str_packet_pure, e.args))

    return bytes_req


def handler_ukcu_generator_simple_rw(log, parsing_data, param_data) -> list:
    code, packet_data = parsing_data
    request_data, response_data, control_gui = param_data
    if code == UKCU_COMMANDS.get(UKCU_SET_SIGNALS):
        return [__str_hex2byte(response_data[0])]
    elif code == UKCU_COMMANDS.get(UKCU_GET_SIGNALS):
        return [__str_hex2byte(response_data[1])]


def handler_request_setup_ukcu(log):
    list_data = list()
    list_data.append(__send_command(UKCU_COMMANDS.get('SetDirection'), 0x0100FF07))
    list_data.append(__send_command(UKCU_COMMANDS.get('SetDirection'), 0x0))
    return list_data


def handler_request_test_ukcu(log):
    p = [0xFE, 0xFD, 0xFB, 0xF7, 0xEF, 0xDF, 0xBF, 0x7F, 0xFF]
    list_data = list()
    for i in p:
        list_data.append(__send_command(UKCU_COMMANDS.get(UKCU_SET_SIGNALS), 0x01000004 | ((i & 0xF0) << 4)))
        list_data.append(__send_command(UKCU_COMMANDS.get(UKCU_SET_SIGNALS), 0x01000000 | ((i & 0xF0) << 4)))
        list_data.append(__send_command(UKCU_COMMANDS.get(UKCU_SET_SIGNALS), 0x01000000 | ((i & 0x0F) << 8)))
        list_data.append(__send_command(UKCU_COMMANDS.get(UKCU_SET_SIGNALS), 0x01000004 | ((i & 0x0F) << 8)))
        list_data.append(__send_command(UKCU_COMMANDS.get(UKCU_SET_SIGNALS), 0x01000A06))
        list_data.append(__send_command(UKCU_COMMANDS.get(UKCU_SET_SIGNALS), 0x01000A02))
        list_data.append(__send_command(UKCU_COMMANDS.get(UKCU_SET_SIGNALS), 0x01000402))
        list_data.append(__send_command(UKCU_COMMANDS.get(UKCU_SET_SIGNALS), 0x01000406))
        list_data.append(__send_command(UKCU_COMMANDS.get(UKCU_SET_SIGNALS), 0x01000004))
        list_data.append(__send_command(UKCU_COMMANDS.get(UKCU_GET_SIGNALS), 0x0000FF00, expected_data=(i << 8)))
    return list_data


def handler_request_reset_ukcu(log):
    list_data = list()
    list_data.append(__send_command(UKCU_COMMANDS.get(UKCU_SET_SIGNALS), 0x01000A04))
    list_data.append(__send_command(UKCU_COMMANDS.get(UKCU_SET_SIGNALS), 0x01000A00))
    list_data.append(__send_command(UKCU_COMMANDS.get(UKCU_SET_SIGNALS), 0x01000500))
    list_data.append(__send_command(UKCU_COMMANDS.get(UKCU_SET_SIGNALS), 0x01000504))
    list_data.append(__send_command(UKCU_COMMANDS.get(UKCU_SET_SIGNALS), 0x01000506))
    list_data.append(__send_command(UKCU_COMMANDS.get(UKCU_SET_SIGNALS), 0x01000502))
    list_data.append(__send_command(UKCU_COMMANDS.get(UKCU_SET_SIGNALS), 0x01000A02))
    list_data.append(__send_command(UKCU_COMMANDS.get(UKCU_SET_SIGNALS), 0x01000A06))
    return list_data

