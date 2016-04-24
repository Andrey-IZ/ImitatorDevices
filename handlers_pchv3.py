#!/usr/bin/env python

from tools_binary import qt_value_to_bytes


def __create_packet(code, data):
    packet = bytearray()
    code = qt_value_to_bytes(code.get('type'), code.get('value'))
    packet.extend(code)
    count_len = 1 + 1   # code + header_len
    if isinstance(data, list):
        for value in data:
            packet.extend(qt_value_to_bytes(value.get('type'), value.get('value')))
            count_len += 1
    else:
        packet.extend(qt_value_to_bytes(data.get('type'), data.get('value')))
        count_len += 1

    packet[:0] = qt_value_to_bytes('quint16', count_len)  # header + code + data
    return bytes(packet)


def handler_pchv3_unversal(response_data) -> [bytes]:
    """
    Generates packet from code and an item of data
    :param response_data:
    :return:
    """
    if isinstance(response_data, dict):
        code = response_data.get('code')
        data = response_data.get('data')
        if isinstance(code, dict) and (isinstance(data, dict) or isinstance(data, list)):
            return [__create_packet(code, data)]
    raise TypeError("Invalid parameters, that divergence signature (not dict): {}".format(response_data))

