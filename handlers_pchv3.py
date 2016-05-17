#!/usr/bin/env python

from tools_binary import qt_value_to_bytes
import struct


def handler_parser_pchv3(bytes_recv):
    if len(bytes_recv) > 4:
        len_packet, code = struct.unpack('!2H', bytes_recv[:4])
        return len_packet, code, bytes_recv
    return None


def __create_packet_qt(code, data):
    packet = bytearray()
    code = qt_value_to_bytes(code.get('type'), code.get('value'))
    packet.extend(code)
    count_len = 1 + 1  # code + header_len
    if isinstance(data, list):
        for value in data:
            packet.extend(qt_value_to_bytes(value.get('type'), value.get('value')))
            count_len += 1
    else:
        packet.extend(qt_value_to_bytes(data.get('type'), data.get('value')))
        count_len += 1

    packet[:0] = qt_value_to_bytes('quint16', count_len)  # header + code + data
    return bytes(packet)


def __create_packet(code, data):
    packet = bytearray()
    code = qt_value_to_bytes('quint16', code)
    packet.extend(code)
    count_len = 1 + 1  # code + header_len
    if isinstance(data, list):
        for value in data:
            packet.extend(qt_value_to_bytes('quint8', value))
            count_len += 1
    else:
        packet.extend(qt_value_to_bytes('quint8', data))
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
            return [__create_packet_qt(code, data)]
    raise TypeError("Invalid parameters, that divergence signature (not dict): {}".format(response_data))


names_power_sources = {0: '5,7В1', 1: '5,7В2', 2: '6В', 3: '7,5В'}


def handler_pchv3_power_changer(log, parsing_data, request_data, response_data) -> [bytes]:
    len_packet, code, bytes_recv = parsing_data
    pchv3_power_source = globals().get('config_vars').get('pchv3_power_source')
    global names_power_sources
    send_data = []
    if code == request_data:
        id_power, turn_on = struct.unpack('!2B', bytes_recv[4:6])
        log.info(
            '+++ Команда: \"{}\" id = \"{}\", turn_on = {}'.format('Питание ИП', names_power_sources.get(id_power),
                                                                   bool(turn_on)))

        code = {'value': code, 'type': 'quint16'}
        data = [{'value': id_power, 'type': 'quint8'}, {'value': turn_on, 'type': 'quint8'}]

        send_data.append(__create_packet_qt(code, data))

        pchv3_power_source[id_power] = bool(turn_on)

        data = {'value': all(pchv3_power_source.values()), 'type': 'quint8'}
        code = {'value': 6, 'type': 'quint16'}
        send_data.append(__create_packet_qt(code, data))
    return send_data


def handler_pchv3_all_power_changer(log, parsing_data, request_data, response_data) -> [bytes]:
    len_packet, code, bytes_recv = parsing_data
    code_ps = response_data
    global names_power_sources
    pchv3_power_source = globals().get('config_vars').get('pchv3_power_source')
    send_data = []
    if code == request_data:
        turn_on = struct.unpack('!B', bytes_recv[4:5])[0]
        log.info('+++ Команда: \"{}\" turn_on = {}'.format('Питание на всех ИП',
                                                           bool(turn_on)))
        for id_power in names_power_sources:
            code_id = {'value': code_ps, 'type': 'quint16'}
            data = [{'value': id_power, 'type': 'quint8'},
                    {'value': turn_on, 'type': 'quint8'}]
            pchv3_power_source[id_power] = bool(turn_on)
            send_data.append(__create_packet_qt(code_id, data))

        code = {'value': code, 'type': 'quint16'}
        data = {'value': turn_on, 'type': 'quint8'}

        send_data.append(__create_packet_qt(code, data))

    return send_data
