#!/usr/bin/env python

from tools_binary import qt_value_to_bytes, value_from_qt_bytes
import struct
import random


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
            b = qt_value_to_bytes(value.get('type'), value.get('value'))
            packet.extend(b)
            count_len += len(b)
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


def handler_pchv3_unversal(log, response_data) -> [bytes]:
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


def handler_pchv3_power_changer(log, parsing_data, param_data) -> [bytes]:
    len_packet, code, bytes_recv = parsing_data
    code_ps, code_ps_all, control_gui = param_data
    if code == code_ps:
        pchv3_power_source = globals().get('config_vars').get('pchv3_power_source')
        names_power_sources = globals().get('config_vars').get('names_power_sources')
        id_power, turn_on = struct.unpack('!2B', bytes_recv[4:6])
        log.info(
            '+++ Команда: "{}" id = "{}", turn_on = {}'.format('Питание ИП', names_power_sources.get(id_power),
                                                               bool(turn_on)))
        pchv3_power_source[id_power] = bool(turn_on)
        return __get_power_state_packet(log, code_ps_all, code_ps)
    return []


def handler_pchv3_all_power_changer(log, parsing_data, param_data) -> [bytes]:
    len_packet, code, bytes_recv = parsing_data
    code_ps, code_ps_all, control_gui = param_data
    if code_ps_all == code:
        pchv3_power_source = globals().get('config_vars').get('pchv3_power_source')
        value = value_from_qt_bytes('quint8', bytes_recv[4:5])
        turn_on = bool(value)
        log.info('+++ Команда: "{}" turn_on = {}'.format('Питание на всех ИП', turn_on))
        for id_power in pchv3_power_source:
            pchv3_power_source[id_power] = turn_on

        return __get_power_state_packet(log, code_ps_all, code_ps)
    return []


def handler_pchv3_get_power_state(log, response_data) -> [bytes]:
    code_ps_all, code_ps = response_data
    return __get_power_state_packet(None, code_ps_all, code_ps)


def __get_power_state_packet(log, code_ps_all, code_ps):
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


def handler_pchv3_power_on_channel(log, parsing_data, param_data) -> [bytes]:
    len_packet, code, bytes_recv = parsing_data
    names_power_tructs = globals().get('config_vars').get('names_power_tructs')
    names_channels = globals().get('config_vars').get('names_channels')
    code_ps = param_data[0]

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


def handler_pchv3_attenuators(log, parsing_data, param_data) -> [bytes]:
    len_packet, code, bytes_recv = parsing_data
    code_ps = param_data[0]
    if code == code_ps:
        if len_packet == 10:
            names_channels = globals().get('config_vars').get('names_channels')
            id_channel = value_from_qt_bytes('quint8', bytes_recv[4:5])
            at1 = value_from_qt_bytes('float', bytes_recv[5:-1])
            at2 = value_from_qt_bytes('quint8', bytes_recv[-1:])
            log.info(
                '+++ Команда: "Установить аттенюаторы":, АТ1 = {}, АТ2 = {}, канал = \"{}\"'.format(at1, at2,
                                                                                                    names_channels.get(
                                                                                                        id_channel)))
            return [__qt_create_packet({'value': code_ps, 'type': 'quint16'},
                                       [{'value': id_channel, 'type': 'quint8'},
                                        {'value': at1, 'type': 'float'},
                                        {'value': at2, 'type': 'quint8'}])]
            # return [bytes_recv]
        log.error('+++ ERROR: Команда: "Установить аттенюаторы": Длина пакета неверная (!= 14)')
    return []


def handler_pchv3_vch_truct(log, parsing_data, param_data) -> [bytes]:
    len_packet, code, bytes_recv = parsing_data
    code_ps = param_data[0]
    if code == code_ps:
        if len_packet == 6:
            names_channels = globals().get('config_vars').get('names_channels')
            names_vch_tructs = globals().get('config_vars').get('names_vch_tructs')
            id_channel = value_from_qt_bytes('quint8', bytes_recv[4:5])
            vch_truct = value_from_qt_bytes('quint8', bytes_recv[-1:])
            log.info(
                '+++ Команда: "Установить аттенюаторы":, ВЧ тракт = {}, канал = \"{}\"'.format(
                    names_vch_tructs.get(vch_truct), names_channels.get(id_channel)))
            return [__qt_create_packet({'value': code_ps, 'type': 'quint16'},
                                       [{'value': id_channel, 'type': 'quint8'},
                                        {'value': vch_truct, 'type': 'quint8'}])]
        log.error('+++ ERROR: Команда: "Установить аттенюаторы": Длина пакета неверная (!= 14)')
    return []


def handler_pchv3_state_aru(log, parsing_data, param_data) -> [bytes]:
    len_packet, code, bytes_recv = parsing_data
    code_ps = param_data[0]
    if code == code_ps:
        if len_packet == 6:
            names_channels = globals().get('config_vars').get('names_channels')
            # names_vch_tructs = globals().get('config_vars').get('names_vch_tructs')
            id_channel = value_from_qt_bytes('quint8', bytes_recv[4:5])
            state_aru = value_from_qt_bytes('quint8', bytes_recv[-1:])
            log.info(
                '+++ Команда: "Установить состояние АРУ тракта":, АРУ = {}, канал = \"{}\"'.format(
                    'выкл' if state_aru == 0 else 'вкл', names_channels.get(id_channel)))
            return [__qt_create_packet({'value': code_ps, 'type': 'quint16'},
                                       [{'value': id_channel, 'type': 'quint8'},
                                        {'value': state_aru, 'type': 'quint8'}])]
            # return [bytes_recv]
        log.error('+++ ERROR: Команда: "Установить состояние АРУ тракта": Длина пакета неверная (!= 6)')
    return []


def handler_pchv3_fapch_codes(log, parsing_data, param_data) -> [bytes]:
    len_packet, code, bytes_recv = parsing_data
    # v= response_data.get_ui_value('Состояние питания', 'Источники питания', 'Мощность', 'spinbox')
    # response_data.set_ui_value('Состояние питания', 'Источники питания', 'Мощность', 'spinbox', 13)

    request_data, response_data, control_gui = param_data
    code_req, code_resp = request_data
    if code == code_req:
        names_channels = globals().get('config_vars').get('names_channels')
        id_channel = value_from_qt_bytes('quint8', bytes_recv[4:5])
        amount_codes = value_from_qt_bytes('quint8', bytes_recv[5:6])
        len_list = len(bytes_recv[6:])
        if amount_codes * 5 != len_list:
            log.error('+++ ERROR: list\'s length is invalid: {} vs {}'.format(amount_codes, len_list))
        list_codes_fapch = []
        for i in range(0, amount_codes, 2):
            reg = value_from_qt_bytes('quint8', bytes_recv[i + 6: i + 7])
            bits = value_from_qt_bytes('quint8', bytes_recv[i + 7: i + 8])
            list_codes_fapch.append(('{0:X}h'.format(reg), '{0:b}'.format(bits)))
        log.info(
            '+++ Команда: "Установить таблицу кодов ФАПЧ": канал = \"{}\" ФАПЧ = "{}"'.format(
                names_channels.get(id_channel), list_codes_fapch))
        return [bytes.fromhex(response_data)]
        # return [__qt_create_packet({'value': code_resp, 'type': 'quint16'},
        #                            [{'value': id_channel, 'type': 'quint8'},
        #                             {'value': True, 'type': 'quint8'}])]
    return []


def handler_pchv3_update_sensors(log, param_data) -> [bytes]:
    response_data, control_gui = param_data
    names_channels = globals().get('config_vars').get('names_channels')

    rand = control_gui.get_ui_value('Сенсоры', 'Обновление сенсоров', 'Random', 'checkbox')
    # response_data.set_ui_value('Состояние питания', 'Источники питания', 'Мощность', 'spinbox', 13)

    t1 = random.randrange(100, 1000) / 10 if rand else control_gui.get_ui_value('Сенсоры', 'Обновление сенсоров', 't1', 'spinbox')
    t2 = random.randrange(100, 1000) / 10 if rand else control_gui.get_ui_value('Сенсоры', 'Обновление сенсоров', 't2', 'spinbox')
    t_top = random.randrange(0, 2) if rand else control_gui.get_ui_value('Сенсоры', 'Обновление сенсоров', 't_top', 'checkbox')
    t_crit = random.randrange(0, 2) if rand else control_gui.get_ui_value('Сенсоры', 'Обновление сенсоров', 't_crit', 'checkbox')
    t_95 = random.randrange(0, 2) if rand else control_gui.get_ui_value('Сенсоры', 'Обновление сенсоров', 't_95', 'checkbox')
    p57v1 = random.randrange(0, 2)
    p57v2 = random.randrange(0, 2)
    p60v = True
    p75v = False
    clk = random.randrange(0, 1)
    count_channel = len(names_channels)
    list_info =[]
    list_sensors = [{'value': count_channel, 'type': 'quint8'}]

    for id_channel in range(len(names_channels)):
        fapch_syn = random.randrange(0, 2)
        fapch_jit = random.randrange(0, 2)
        acp = random.randrange(10, 500) / 10
        list_info.extend([{'fapch_syn':fapch_syn, 'fapch_jit':fapch_jit, 'acp': acp}])

        list_sensors.append({'value': fapch_syn, 'type': 'bool'})
        list_sensors.append({'value': fapch_jit, 'type': 'bool'})
        list_sensors.append({'value': acp, 'type': 'float'})

    log.info('Данные: t1={}, t2={}, t_top={}, t_crit={}, t_95={}, p57v1={}, p57v2={}, p60v={}, p75v={}, clk={}'.format(
             t1, t2, t_top, t_crit, t_95, p57v1, p57v2, p60v, p75v, clk))

    code = {'value': 2, 'type': 'quint16'}
    data = [{'value': t1, 'type': 'float'},
            {'value': t2, 'type': 'float'},
            {'value': t_top, 'type': 'quint8'},
            {'value': t_crit, 'type': 'quint8'},
            {'value': t_95, 'type': 'quint8'},
            {'value': p57v1, 'type': 'quint8'},
            {'value': p57v2, 'type': 'quint8'},
            {'value': p60v, 'type': 'quint8'},
            {'value': p75v, 'type': 'quint8'},
            {'value': clk, 'type': 'quint8'},
            ]
    data.extend(list_sensors)
    log.info(
        '+++ Команда: "Обновление сенсоров": канал = \"{}\" StateSensors = "{}"'.format(
            names_channels.get(id_channel), list_info))
    return [__qt_create_packet(code, data)]


def handler_pchv3_set_cap(log, parsing_data, param_data) -> [bytes]:
    len_packet, code, bytes_recv = parsing_data
    request_data, response_data, control_gui = param_data
    names_channels = globals().get('config_vars').get('names_channels')
    code_ps = request_data
    if code == code_ps:
        if len_packet == 7:
            id_channel = value_from_qt_bytes('quint8', bytes_recv[4:5])
            code_cap = value_from_qt_bytes('qint16', bytes_recv[5:7])
            log.info(
                '+++ Команда: "Установить код ЦАП":, код = {}, канал = \"{}\"'.format(
                    code_cap, names_channels.get(id_channel)))
            if code_cap == 1:
                code_cap = -1
            return [__qt_create_packet({'value': code_ps, 'type': 'quint16'},
                                       [{'value': id_channel, 'type': 'quint8'},
                                        {'value': code_cap, 'type': 'qint16'}])]
    return []


def gui_handler_pchv3_state_aru(log, parsing_data, param_data) -> [bytes]:
    len_packet, code, bytes_recv = parsing_data
    request_data, response_data, control_gui = param_data
    names_channels = globals().get('config_vars').get('names_channels')
    # names_vch_tructs = globals().get('config_vars').get('names_vch_tructs')
    code_ps = request_data
    if code == code_ps:
        if len_packet == 6:
            id_channel = value_from_qt_bytes('quint8', bytes_recv[4:5])
            state_aru = value_from_qt_bytes('quint8', bytes_recv[-1:])
            log.info(
                '+++ Команда: "Установить состояние АРУ тракта":, АРУ = {}, канал = \"{}\"'.format(
                    'выкл' if state_aru == 0 else 'вкл', names_channels.get(id_channel)))
            return [__qt_create_packet({'value': code_ps, 'type': 'quint16'},
                                       [{'value': id_channel, 'type': 'quint8'},
                                        {'value': state_aru, 'type': 'quint8'}])]
            # return [bytes_recv]
        log.error('+++ ERROR: Команда: "Установить состояние АРУ тракта": Длина пакета неверная (!= 6)')
    return []
