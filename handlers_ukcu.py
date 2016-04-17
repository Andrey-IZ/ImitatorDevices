#!/usr/bin/env python
from math import log
import struct


def sizeof(n):
    if n == 0:
        return 1
    return int(log(n, 256)) + 1


commands = dict(SetDirection=0x01B, SetSignals=0x11B, GetSignals=0x21B)


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


def send_command(code, data, expected_data=0, timeout=0):
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
    :return:  array's bytes for will send to PC again
    """
    packet = UkcuPacket()
    derived_bytes = request_data[0]
    code = request_data[2]
    expected_data = request_data[3]

    if not packet.parse(derived_bytes):
        raise ValueError("Invalid packet data is derived here")

    packet = UkcuPacket(code | 4, expected_data)
    return packet.to_bytes()


def handler_request_read_low():
    list_data = list()
    list_data.append(send_command(commands.get('SetSignals'), 0x01000004))
    list_data.append(send_command(commands.get('GetSignals'), 0x0000FF00))
    return list_data


def handler_request_read_high():
    list_data = list()
    list_data.append(send_command(commands.get('SetSignals'), 0x01000006))
    list_data.append(send_command(commands.get('GetSignals'), 0x0000FF00))
    return list_data


def handler_request_write(request_data):
    """
    Operates packet commands from PC to serial port device
    :param request_data:
    :return:
    """
    list_data = [send_command(commands.get('SetSignals'), 0x01000004 | (request_data & 0x00F0) << 4),
                 send_command(commands.get('SetSignals'), 0x01000000 | (request_data & 0x00F0) << 4),
                 send_command(commands.get('SetSignals'), 0x01000000 | (request_data & 0x000F) << 8),
                 send_command(commands.get('SetSignals'), 0x01000004 | (request_data & 0x000F) << 8),
                 send_command(commands.get('SetSignals'), 0x01000006 | (request_data & 0xF000) >> 4),
                 send_command(commands.get('SetSignals'), 0x01000002 | (request_data & 0xF000) >> 4),
                 send_command(commands.get('SetSignals'), 0x01000002 | (request_data & 0x0F00)),
                 send_command(commands.get('SetSignals'), 0x01000006 | (request_data & 0x0F00))]
    return list_data


def handler_request_write_read_low(request_data):
    list_data = list()
    list_data.append(handler_request_write(request_data))
    list_data.append(handler_request_read_low())
    return list_data


def handler_request_setup_ukcu():
    list_data = list()
    list_data.append(send_command(commands.get('SetDirection'), 0x0100FF07))
    list_data.append(send_command(commands.get('SetDirection'), 0x0))
    return list_data


def handler_request_test_ukcu():
    p = [0xFE, 0xFD, 0xFB, 0xF7, 0xEF, 0xDF, 0xBF, 0x7F, 0xFF]
    list_data = list()
    for i in p:
        list_data.append(send_command(commands.get('SetSignals'), 0x01000004 | ((i & 0xF0) << 4)))
        list_data.append(send_command(commands.get('SetSignals'), 0x01000000 | ((i & 0xF0) << 4)))
        list_data.append(send_command(commands.get('SetSignals'), 0x01000000 | ((i & 0x0F) << 8)))
        list_data.append(send_command(commands.get('SetSignals'), 0x01000004 | ((i & 0x0F) << 8)))
        list_data.append(send_command(commands.get('SetSignals'), 0x01000A06))
        list_data.append(send_command(commands.get('SetSignals'), 0x01000A02))
        list_data.append(send_command(commands.get('SetSignals'), 0x01000402))
        list_data.append(send_command(commands.get('SetSignals'), 0x01000406))
        list_data.append(send_command(commands.get('SetSignals'), 0x01000004))
        list_data.append(send_command(commands.get('GetSignals'), 0x0000FF00, expected_data=(i << 8)))
    return list_data


def handler_request_reset_ukcu():
    list_data = list()
    list_data.append(send_command(commands.get('SetSignals'), 0x01000A04))
    list_data.append(send_command(commands.get('SetSignals'), 0x01000A00))
    list_data.append(send_command(commands.get('SetSignals'), 0x01000500))
    list_data.append(send_command(commands.get('SetSignals'), 0x01000504))
    list_data.append(send_command(commands.get('SetSignals'), 0x01000506))
    list_data.append(send_command(commands.get('SetSignals'), 0x01000502))
    list_data.append(send_command(commands.get('SetSignals'), 0x01000A02))
    list_data.append(send_command(commands.get('SetSignals'), 0x01000A06))
    return list_data


if __name__ == '__main__':
    print(handler_request_write(0xA600))
    print(handler_request_read_low())
    print(handler_request_read_high())
    print(handler_request_reset_ukcu())
    print(handler_request_setup_ukcu())
    print(handler_request_test_ukcu())
