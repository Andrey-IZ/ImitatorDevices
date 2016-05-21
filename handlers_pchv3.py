#!/usr/bin/env python

from tools_binary import qt_value_to_bytes, value_from_qt_bytes
import struct


def handler_parser_pchv3(bytes_recv):
    if len(bytes_recv) > 4:
        len_packet, code = struct.unpack('!2H', bytes_recv[:4])
        return len_packet + 2, code, bytes_recv
    return None


def __qt_create_packet(code, data):
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
            return [__qt_create_packet(code, data)]
    raise TypeError("Invalid parameters, that divergence signature (not dict): {}".format(response_data))


def handler_pchv3_power_changer(log, parsing_data, request_data, response_data) -> [bytes]:
    len_packet, code, bytes_recv = parsing_data
    pchv3_power_source = globals().get('config_vars').get('pchv3_power_source')
    names_power_sources = globals().get('config_vars').get('names_power_sources')
    code_ps_all, code_ps = response_data, request_data
    if code == code_ps:
        id_power, turn_on = struct.unpack('!2B', bytes_recv[4:6])
        log.info(
            '+++ Команда: \"{}\" id = \"{}\", turn_on = {}'.format('Питание ИП', names_power_sources.get(id_power),
                                                                   bool(turn_on)))
        pchv3_power_source[id_power] = bool(turn_on)
        return get_power_state_packet(log, code_ps_all, code_ps)
    return []


def handler_pchv3_all_power_changer(log, parsing_data, request_data, response_data) -> [bytes]:
    len_packet, code, bytes_recv = parsing_data
    pchv3_power_source = globals().get('config_vars').get('pchv3_power_source')
    code_ps_all, code_ps = request_data, response_data
    if code_ps_all == code:
        turn_on = qt_value_to_bytes('quint8', bytes_recv[4])
        turn_on = bool(turn_on)
        log.info('+++ Команда: \"{}\" turn_on = {}'.format('Питание на всех ИП', turn_on))
        for id_power in pchv3_power_source:
            pchv3_power_source[id_power] = turn_on

        return get_power_state_packet(log, code_ps_all, code_ps)
    return []


def get_power_state_packet(log, code_ps_all, code_ps):
    send_data = []
    names_power_sources = globals().get('config_vars').get('names_power_sources')
    pchv3_power_source = globals().get('config_vars').get('pchv3_power_source')

    for id_power in names_power_sources:
        code_id = {'value': code_ps, 'type': 'quint16'}
        data = [{'value': id_power, 'type': 'quint8'},
                {'value': pchv3_power_source[id_power], 'type': 'quint8'}]
        send_data.append(__qt_create_packet(code_id, data))
    code_ps_all = {'value': code_ps_all, 'type': 'quint16'}
    data = {'value': all(pchv3_power_source.values()), 'type': 'quint8'}
    send_data.append(__qt_create_packet(code_ps_all, data))
    return send_data


def handler_pchv3_power_on_channel(log, parsing_data, request_data, response_data) -> [bytes]:
    len_packet, code, bytes_recv = parsing_data
    names_power_tructs = globals().get('config_vars').get('names_power_tructs')
    names_channels = globals().get('config_vars').get('names_channels')
    code_ps = request_data
    if code == code_ps:
        id_channel, id_truct, turn_on = struct.unpack('!3B', bytes_recv[4:7])

        log.info(
            '+++ Команда: \"Питание {}\", вкл = {}, канал = \"{}\"'.format(names_power_tructs.get(id_truct),
                                                                           bool(turn_on),
                                                                           names_channels.get(id_channel)))
        return [__qt_create_packet({'value': code_ps, 'type': 'quint16'},
                                   [{'value': id_channel, 'type': 'quint8'},
                                    {'value': id_truct, 'type': 'quint8'},
                                    {'value': turn_on, 'type': 'quint8'}])]
        # return [bytes_recv]
    return []


def handler_pchv3_attenuators(log, parsing_data, request_data, response_data) -> [bytes]:
    len_packet, code, bytes_recv = parsing_data
    names_channels = globals().get('config_vars').get('names_channels')
    code_ps = request_data
    if code == code_ps:
        if len_packet == 14:
            id_channel = value_from_qt_bytes('quint8', bytes_recv[4:5])
            at1 = value_from_qt_bytes('double', bytes_recv[5:-1])
            at2 = value_from_qt_bytes('quint8', bytes_recv[-1:])
            log.info(
                '+++ Команда: "Установить аттенюаторы":, АТ1 = {}, АТ2 = {}, канал = \"{}\"'.format(at1, at2,
                                                                                                    names_channels.get(
                                                                                                        id_channel)))
            return [__qt_create_packet({'value': code_ps, 'type': 'quint16'},
                                       [{'value': id_channel, 'type': 'quint8'},
                                        {'value': at1, 'type': 'double'},
                                        {'value': at2, 'type': 'quint8'}])]
            # return [bytes_recv]
        log.error('+++ ERROR: Команда: "Установить аттенюаторы": Длина пакета неверная (!= 14)')
    return []


def handler_pchv3_vch_truct(log, parsing_data, request_data, response_data) -> [bytes]:
    len_packet, code, bytes_recv = parsing_data
    names_channels = globals().get('config_vars').get('names_channels')
    names_vch_tructs = globals().get('config_vars').get('names_vch_tructs')
    code_ps = request_data
    if code == code_ps:
        if len_packet == 6:
            id_channel = value_from_qt_bytes('quint8', bytes_recv[4:5])
            vch_truct = value_from_qt_bytes('quint8', bytes_recv[-1:])
            log.info(
                '+++ Команда: "Установить аттенюаторы":, ВЧ тракт = {}, канал = \"{}\"'.format(
                    names_vch_tructs.get(vch_truct), names_channels.get(id_channel)))
            return [__qt_create_packet({'value': code_ps, 'type': 'quint16'},
                                       [{'value': id_channel, 'type': 'quint8'},
                                        {'value': vch_truct, 'type': 'quint8'}])]
            # return [bytes_recv]
        log.error('+++ ERROR: Команда: "Установить аттенюаторы": Длина пакета неверная (!= 14)')
    return []
