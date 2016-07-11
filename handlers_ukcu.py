#!/usr/bin/env python

import struct
import re
from tools_binary import str_hex2byte

UKCU_SET_SIGNALS, UKCU_GET_SIGNALS, UKCU_SET_DIRECTION = 'SetSignals', 'GetSignals', 'SetDirection'

UKCU_COMMANDS = {UKCU_SET_DIRECTION: 0x01B, UKCU_SET_SIGNALS: 0x11B, UKCU_GET_SIGNALS: 0x21B}
UKCU_RESP_SET, UKCU_RESP_REPLY = 0x11F, 0x21F
UKCU_READ_LOW_ADDRESS, UKCU_READ_HIGH_ADDRESS = 0x1000004, 0x1000006
UKCU_R_MASK = 0xFF00


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


# def __handler_request_read_low(log):
#     list_data = list()
#     list_data.append(__send_command(UKCU_COMMANDS.get(UKCU_SET_SIGNALS), 0x01000004))
#     list_data.append(__send_command(UKCU_COMMANDS.get(UKCU_GET_SIGNALS), 0x0000FF00))
#     return list_data
#
#
# def __handler_request_read_high(log):
#     list_data = list()
#     list_data.append(__send_command(UKCU_COMMANDS.get(UKCU_SET_SIGNALS), 0x01000006))
#     list_data.append(__send_command(UKCU_COMMANDS.get(UKCU_GET_SIGNALS), 0x0000FF00))
#     return list_data


def __extract_packet_recv(ukcu_shell_packets):
    if len(ukcu_shell_packets) == 8:
        d11 = ukcu_shell_packets[0] - 0x01000004 >> 8
        d21 = (ukcu_shell_packets[2] - 0x01000000) >> 8
        d31 = ukcu_shell_packets[4] - 0x01000006 >> 8
        d41 = ukcu_shell_packets[6] - 0x01000002 >> 8
        n = d31 << 12 | d11 << 4 | d41 << 8 | d21
        return n
    return None


def handler_parser_ucku(log, bytes_recv):
    packet = UkcuPacket()
    if packet.parse(bytes_recv):
        ukcu_clear_shell_packets = globals().get('config_vars').get('ukcu_clear_shell_packets')
        ukcu_shell_packets = globals().get('config_vars').get('ukcu_shell_packets')
        ukcu_code_patch = globals().get('config_vars').get('ukcu_code_patch')
        code_req = None
        if ukcu_clear_shell_packets[0]:
            ukcu_shell_packets.clear()
            # ukcu_code_patch[1] = True
            ukcu_code_patch[0] = 0
            ukcu_clear_shell_packets[0] = False
            log.info('list cleared = {}'.format(ukcu_shell_packets))
        if len(ukcu_shell_packets) == 8:
            ukcu_code_patch[0] = __extract_packet_recv(ukcu_shell_packets)
            log.error(' --- CODE = {}'.format(hex(ukcu_code_patch[0])))
        ukcu_shell_packets.append(packet.data)
        return packet.code, packet.data
    return None


def handler_ukcu_reply_kvitok(log, parsing_data, param_data) -> list:
    code, packet_data = parsing_data
    request_data, response_data, control_gui = param_data
    if code == UKCU_COMMANDS.get(UKCU_SET_SIGNALS):
        return [str_hex2byte(response_data)]  # code: 0x011F,  data: 0x1000100


def handler_ukcu_generate_rw(log, parsing_data, param_data) -> list:
    # code, packet_data = parsing_data
    request_data, response_data, control_gui = param_data
    ukcu_code_patch = globals().get('config_vars').get('ukcu_code_patch')
    ukcu_shell_packets = globals().get('config_vars').get('ukcu_shell_packets')
    if ukcu_code_patch[0] == request_data[0]:
        ukcu_clear_shell_packets = globals().get('config_vars').get('ukcu_clear_shell_packets')

        if isinstance(response_data, list) and len(response_data) == 2:
            if ukcu_shell_packets[-2] == UKCU_READ_LOW_ADDRESS:
                data = response_data[0]
            elif ukcu_shell_packets[-2] == UKCU_READ_HIGH_ADDRESS:
                data = response_data[1]
            if len(ukcu_shell_packets) == 12:
                ukcu_clear_shell_packets[0] = True
        else:
            data = UKCU_RESP_REPLY if response_data is None else response_data
            ukcu_clear_shell_packets[0] = True

        data_hex = hex(data)[2:].upper()
        cmd_hex = hex(ukcu_code_patch[0])[2:].upper()
        if ukcu_shell_packets[-2] == UKCU_READ_LOW_ADDRESS:
            log.error('* Ответ на "0x{}" чтение мл. адреса: 0x{}'.format(cmd_hex, data_hex))
        elif ukcu_shell_packets[-2] == UKCU_READ_HIGH_ADDRESS:
            log.error('* Ответ на "0x{}" чтение стар. адреса: 0x{}'.format(cmd_hex, data_hex))

        return [UkcuPacket(UKCU_RESP_REPLY, data << 8).to_bytes()]


def handler_ukcu_generate_channel_rw(log, parsing_data, param_data) -> list:
    request_data, response_data, control_gui = param_data
    code, packet_data = parsing_data
    ukcu_code_patch = globals().get('config_vars').get('ukcu_code_patch')
    if ukcu_code_patch[0] in list(range(request_data[0], request_data[0] + 8)):
        return handler_ukcu_generate_rw(log, parsing_data, (ukcu_code_patch, response_data, control_gui))


# def handler_ukcu_generator_rw(log, parsing_data, param_data) -> list:
#     """
#     :return: UkcuPacket
#     """
#     code, packet_data = parsing_data
#     request_data, response_data, control_gui = param_data
#
#     if isinstance(request_data, list) and len(request_data):
#         ukcu_shell_packets = globals().get('config_vars').get('ukcu_shell_packets')
#         ukcu_code_patch = globals().get('config_vars').get('ukcu_code_patch')
#         ukcu_clear_shell_packets = globals().get('config_vars').get('ukcu_clear_shell_packets')
#
#         if ukcu_code_patch[1] or request_data[0] == ukcu_code_patch[0]:
#             ukcu_code_patch[0] = request_data[0]
#             ukcu_code_patch[1] = False
#             ukcu_answer_code_data = globals().get('config_vars').get('ukcu_answer_code_data')
#             answer_code, answer_data = ukcu_answer_code_data
#
#             len_packets = len(ukcu_shell_packets)
#
#             if len_packets <= 8:
#                 if code == UKCU_COMMANDS.get(UKCU_SET_SIGNALS):
#                     log.info('+++ Обработана команда {} из {}'.format(len_packets, 8))
#                     if len(ukcu_shell_packets) == 8:
#                         ukcu_code_patch[2] = __extract_packet_recv(ukcu_shell_packets)
#                         if ukcu_code_patch[2] == ukcu_code_patch[0]:
#                             log.error('++++ Распознана команда: 0x{} ("{}")\n'.format(
#                                 hex(ukcu_code_patch[2])[2:].upper(), request_data[1]))
#                         if response_data is None:
#                             ukcu_clear_shell_packets[0] = True
#                     return [UkcuPacket(answer_code, answer_data).to_bytes()]
#             elif code == UKCU_COMMANDS.get(UKCU_SET_SIGNALS) and len_packets in (9, 11):
#                 data_hex = hex(packet_data)[2:].upper()
#                 cmd_hex = hex(ukcu_code_patch[0])[2:].upper()
#                 if packet_data == UKCU_READ_LOW_ADDRESS:
#                     log.error(' "0x{}" запрос чтение мл. адреса: 0x{}'.format(cmd_hex, data_hex))
#                 elif packet_data == UKCU_READ_HIGH_ADDRESS:
#                     log.error(' "0x{}: запрос чтение стар. адреса: 0x{}'.format(cmd_hex, data_hex))
#                 return [UkcuPacket(answer_code, answer_data).to_bytes()]
#             elif code == UKCU_COMMANDS.get(UKCU_GET_SIGNALS) and len_packets in (10, 12) and packet_data == UKCU_R_MASK:
#                 if isinstance(response_data, list) and len(response_data) == 2:
#                     if ukcu_shell_packets[-2] == UKCU_READ_LOW_ADDRESS:
#                         data = response_data[0]
#                     elif ukcu_shell_packets[-2] == UKCU_READ_HIGH_ADDRESS:
#                         data = response_data[1]
#                     if len_packets == 12:
#                         ukcu_clear_shell_packets[0] = True
#                 else:
#                     data = answer_data if response_data is None else response_data
#                     ukcu_clear_shell_packets[0] = True
#
#                 data_hex = hex(data)[2:].upper()
#                 cmd_hex = hex(ukcu_code_patch[0])[2:].upper()
#                 if ukcu_shell_packets[-2] == UKCU_READ_LOW_ADDRESS:
#                     log.error('* Ответ на "0x{}" чтение мл. адреса: 0x{}'.format(cmd_hex, data_hex))
#                 elif ukcu_shell_packets[-2] == UKCU_READ_HIGH_ADDRESS:
#                     log.error('* Ответ на "0x{}" чтение стар. адреса: 0x{}'.format(cmd_hex, data_hex))
#
#                 ukcu_answer_resp_code = globals().get('config_vars').get('ukcu_answer_resp_code')
#                 return [UkcuPacket(ukcu_answer_resp_code, data << 8).to_bytes()]
#         elif len(ukcu_shell_packets) == 8 and request_data[0] == ukcu_code_patch[2]:
#             log.error(' +++ Распознана команда: 0x{} ("{}")\n'.format(hex(ukcu_code_patch[2])[2:].upper(),
#                                                                       request_data[1]))
#             ukcu_code_patch[0] = ukcu_code_patch[2]
#             if response_data is None:
#                 ukcu_clear_shell_packets[0] = True
#
#
# def handler_request_write_read_low(log, parsing_data, param_data):
#     bytes_recv = parsing_data
#     request_data, response_data, control_gui = param_data
#     list_data = list()
#     list_data.extend(handler_ukcu_generator_rw(log, parsing_data, param_data))
#     list_data.extend(__handler_request_read_low(log))
#     return list_data


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


if __name__ == '__main__':
    # print(handler_gen_request_write(0xA600))
    # print(__handler_request_read_low())
    # print(__handler_request_read_high())
    # print(handler_request_reset_ukcu())
    # print(handler_request_setup_ukcu())
    # print(handler_request_test_ukcu())
    pass
