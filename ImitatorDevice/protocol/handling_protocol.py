#!/usr/bin/env python

import time
from ImitatorDevice.protocol.tools_parse_yaml_protocol import str_hex2byte, load_handler, \
    load_conf_test, str_dict_keys_lower
from ImitatorDevice.socket.socket_settings import SocketSettings
from ImitatorDevice.serial.serial_port_settings import SerialPortSettings

CH_ESTRIGGER_CON, CH_ESTRIGGER_TIMEOUT = ('on_connection', 'on_timeout')
CH_ORDER_GENERATOR, CH_ORDER_ZIP, CH_ORDER_SEMIDUPLEX, CH_ORDER_GENERATOR_FULL = (
    'generator', 'zip', 'semiduplex', 'full-generator')
KW_DOC, KW_RESPONSE, KW_REQUEST, KW_EMITSEND, KW_EMIT_TRIGGER, KW_EMIT_TIMEOUT, KW_HANDLER_RESPONSE, KW_HANDLER_REQUEST = (
    'doc', 'response', 'request', 'emit_send', 'trigger', 'timeout', 'handler_response', 'handler_request')
KW_ORDER, KWDELAY_RESPONSE = ('order', 'delay_response')


class HandlingProtocol(object):
    """
    It implements  parsing and algorithmic handling loaded protocol configuration
    """

    def __init__(self, logger):
        self.__serial_port_settings = []
        self.__socket_settings = []
        self.log = logger
        self.config_vars = {}

        self.__lists_protocol = []
        self.__count_req_generator_packet = 0
        self.__count_req_zip_packet = 0
        self.__count_req_semiduplex_packet = 0
        self.__count_protocol = 0
        self.__len_list_protocol = 0
        self.__is_processing_resp = False

        self.__list_emit_send = {CH_ESTRIGGER_CON: [[], [], []], CH_ESTRIGGER_TIMEOUT: [[], [], []]}
        self.__len_list_emit_send = {CH_ESTRIGGER_CON: 0, CH_ESTRIGGER_TIMEOUT: 0}
        self.__time_begin_emit_send = time.time()

        self.__handler_dict_parser = {}
        self.__list_gen_full = []
        self.__dict_emit_send_full_gen_timeout = {}

    @property
    def is_emit_send_on_connect(self):
        return self.__len_list_emit_send[CH_ESTRIGGER_CON] > 0

    @property
    def is_emit_send_on_timeout(self):
        return self.__len_list_emit_send[CH_ESTRIGGER_TIMEOUT] > 0

    @property
    def serialport_settings(self):
        """

        :return: dictionary interface, generating from class PortSettings
        """
        return self.__serial_port_settings

    @serialport_settings.setter
    def serialport_settings(self, value):
        """

        :param value: dictionary interface, generating from class PortSettings
        :return:
        """
        self.__port_settings = value

    @property
    def socket_settings(self):
        """

        :return: dictionary interface, generating from class PortSettings
        """
        return self.__socket_settings

    @socket_settings.setter
    def socket_settings(self, value):
        """

        :param value: dictionary interface, generating from class PortSettings
        :return:
        """
        self.__port_settings = value

    @staticmethod
    def __parse_interface(settings, class_settings):
        obj = class_settings()
        obj.parse(settings)
        return obj

    def __parse_settings(self, conf_settings):
        conf_settings = str_dict_keys_lower(conf_settings)
        self.__socket_settings = self.__parse_interface(conf_settings.get('socketsettings'), SocketSettings)
        self.__serial_port_settings = self.__parse_interface(conf_settings.get('serialsettings'), SerialPortSettings)

    def handler_emit_send(self, is_connect=False, is_timeout=False) -> [bytes]:
        if self.is_emit_send_on_connect and is_connect:
            self.log.warning('!WARNING: Emit send packets on connection: '
                             '{}'.format(self.__list_emit_send[CH_ESTRIGGER_CON][1]))
            send_list = []
            list_index_emit_con = self.__list_emit_send[CH_ESTRIGGER_CON][2]
            list_send_gen, list_index_gen = self.__process_full_generate_response()
            tm = time.time()
            for i in range(max(list_index_emit_con, list_index_gen)[0] + 1):
                if list_index_gen and i in list_index_gen:
                    send_list.extend(list_send_gen)
                if list_index_emit_con and i in list_index_emit_con:
                    send_list.extend(self.__list_emit_send[CH_ESTRIGGER_CON][0])
                    if self.__len_list_emit_send[CH_ESTRIGGER_TIMEOUT]:
                        n = list_index_emit_con.index(i)
                        self.__list_emit_send[CH_ESTRIGGER_TIMEOUT][1][n] = tm
            # self.register_time_send_on_connect()
            return send_list

        if self.is_emit_send_on_timeout and is_timeout:
            list_emit_send = []
            docs = []
            for i, (timeout, list_send, doc, order) in enumerate(self.__list_emit_send[CH_ESTRIGGER_TIMEOUT][0]):
                if time.time() - self.__list_emit_send[CH_ESTRIGGER_TIMEOUT][1][i] >= timeout:
                    list_emit_send.extend(list_send)
                    docs.append((doc, order))
                    self.__list_emit_send[CH_ESTRIGGER_TIMEOUT][1][i] = time.time()
                    self.log.warning('!WARNING: Emit send packet on timeout = {} sec: {}'.format(timeout, docs))
            if list_emit_send:
                return list_emit_send
        return []

    def __parse_emit_send(self, dict_emit, handler_dict_response, response, param_info):
        if isinstance(dict_emit, dict):
            trigger = dict_emit.get(KW_EMIT_TRIGGER, '')
            doc, order, index_conf = param_info
            if trigger:
                try:
                    list_send = self.__genearate_list_packet(handler_dict_response, response, param_info)
                except Exception as err:
                    raise ValueError(err) from err
                if list_send:
                    if isinstance(trigger, list):
                        for trig in trigger:
                            self.__add_list_emit_send(dict_emit, doc, order, list_send, trig, index_conf)
                    elif isinstance(trigger, str):
                        trigger = trigger.lower().strip()
                        self.__add_list_emit_send(dict_emit, doc, order, list_send, trigger, index_conf)
            else:
                raise ValueError('!Error: trigger into emit_send is not unknown: {}',
                                 dict_emit.get(KW_EMIT_TRIGGER, ''))
        return None

    def __add_list_emit_send(self, dict_emit, doc, order, list_send, trigger, index_conf):
        if order != CH_ORDER_GENERATOR_FULL:
            if trigger == CH_ESTRIGGER_CON:  # on_connection
                self.__list_emit_send[CH_ESTRIGGER_CON][0].extend(list_send)
                self.__list_emit_send[CH_ESTRIGGER_CON][1].append([doc, order])
                self.__list_emit_send[CH_ESTRIGGER_CON][2].append(index_conf)
            if trigger == CH_ESTRIGGER_TIMEOUT:  # on_timeout
                timeout = dict_emit.get(KW_EMIT_TIMEOUT, 1)
                self.__list_emit_send[CH_ESTRIGGER_TIMEOUT][0].append([timeout, list_send, doc, order])
                self.__list_emit_send[CH_ESTRIGGER_TIMEOUT][2].append(index_conf)
            elif trigger != CH_ESTRIGGER_CON:
                raise ValueError('!Error: trigger into emit_send is unknown: doc={}, trigger={}; timeout={}'.format(
                    doc, trigger, dict_emit.get(KW_EMIT_TIMEOUT, '')))

    def __init_parse(self):
        self.__lists_protocol.clear()

        self.__list_emit_send[CH_ESTRIGGER_TIMEOUT][0].clear()
        self.__list_emit_send[CH_ESTRIGGER_TIMEOUT][1].clear()
        self.__list_emit_send[CH_ESTRIGGER_TIMEOUT][2].clear()
        self.__len_list_emit_send[CH_ESTRIGGER_TIMEOUT] = 0

        self.__len_list_emit_send[CH_ESTRIGGER_CON] = 0
        self.__list_emit_send[CH_ESTRIGGER_CON][0].clear()
        self.__list_emit_send[CH_ESTRIGGER_CON][1].clear()
        self.__list_emit_send[CH_ESTRIGGER_CON][2].clear()

        self.__dict_emit_send_full_gen_timeout.clear()

    def __process_full_generate_response_with_parser(self, bytes_recv):
        if not self.__handler_dict_parser:
            return None
        list_send_data = []
        list_index = []
        func_parser = load_handler(self.config_vars, **self.__handler_dict_parser)
        for handler_dict_response, request, response, doc, order, index, is_emit in self.__list_gen_full:
            if isinstance(handler_dict_response, dict) and not is_emit:
                list_func_handler_response = load_handler(self.config_vars, **handler_dict_response)
                for func_handler_response in list_func_handler_response:
                    func_list_result = func_handler_response(self.log, func_parser[0](bytes_recv), request, response)
                    if func_list_result and isinstance(func_list_result, (list, tuple)):
                        self.log.warning(
                            u'!WARNING Handled command: "{0}", function = \"{3}\", order = {1}, index={2}'.format(
                                doc, order, index, func_handler_response.__name__))
                        list_send_data.extend(func_list_result)
                        list_index.append(index)
        return list_send_data, list_index

    def __process_full_generate_response(self):
        list_send_data = []
        list_index = []
        try:
            for handler_dict_response, request, response, doc, order, index, is_emit in self.__list_gen_full:
                if isinstance(handler_dict_response, dict) and is_emit:
                    list_func_handler_response = load_handler(self.config_vars, **handler_dict_response)
                    for func_handler_response in list_func_handler_response:
                        func_list_result = func_handler_response(self.log, request, response)
                        if func_list_result and isinstance(func_list_result, (list, tuple)):
                            self.log.warning(
                                u'!WARNING Handled command: "{0}", function = \"{3}\", order = {1}, index={2}'.format(
                                    doc, order, index, func_handler_response.__name__))
                        list_index.append(index)
                        list_send_data.extend(func_list_result)
        except Exception as err:
            raise Exception('{}; doc = {}'.format(err, (doc, order, index))) from err
        return list_send_data, list_index

    def parse(self, file_name):
        """
        It makes parsing file_name and generates lists of protocol
        :param file_name:
        :return:
        """
        conf = load_conf_test(file_name)
        settings_conf = conf[0]
        self.__parse_settings(settings_conf)
        self.__init_parse()

        cmd = str_dict_keys_lower(settings_conf)

        self.config_vars = cmd.get('config_vars', {})
        if isinstance(cmd, dict):
            parser = cmd.get('handler_parser')
            if parser:
                self.__handler_dict_parser = parser

        for i, cmd in enumerate(conf[1:]):
            cmd = str_dict_keys_lower(cmd)
            if not cmd:
                continue
            doc = cmd.get(KW_DOC)
            if not isinstance(doc, str) and not doc:
                raise ValueError(
                    u"Parse error: in conf didn't find parameter doc or it is empty: command = {}".format(i))
            doc = doc.strip()

            handler_response = cmd.get(KW_HANDLER_RESPONSE)
            response = cmd.get(KW_RESPONSE)
            order = cmd.get(KW_ORDER, CH_ORDER_ZIP).lower()
            request = cmd.get(KW_REQUEST)

            emit_send = cmd.get(KW_EMITSEND, '')

            if order == CH_ORDER_GENERATOR_FULL:
                self.__list_gen_full.append((handler_response, request, response, doc, order, i, emit_send != ''))
                continue
            if emit_send != '':
                try:
                    self.__parse_emit_send(cmd.get(KW_EMITSEND), handler_response, response, (doc, order, i))
                except Exception as err:
                    self.log.error(err)
                    raise Exception(str(err) + 'on index = {}'.format(i)) from err
                continue

            handler_request = cmd.get(KW_HANDLER_REQUEST)

            list_req = self.__genearate_list_packet(handler_request, request, (doc, order, i))
            if len(list_req) == 0:
                raise ValueError("Parse error: packet loaded nothing for: {0}".format(doc))

            gen_list_resp = self.__generate_list_response(handler_response, order, response, (doc, order))
            if order != CH_ORDER_SEMIDUPLEX and isinstance(gen_list_resp, list) and len(list_req) != len(gen_list_resp):
                raise ValueError("!! Error: Generating lists for responses and requests is not equal: "
                                 "{0} vs {1}, doc = '{2}', order = {3}".format(len(gen_list_resp), len(list_req), doc,
                                                                               order))
            self.__lists_protocol.append((order, list_req, gen_list_resp, doc))

        if self.__lists_protocol and isinstance(self.__lists_protocol[0], tuple) and len(self.__lists_protocol) > 0:
            list_unique = []
            for row in self.__lists_protocol:
                if isinstance(row, bytes):
                    list_unique.append(row)
                elif isinstance(row[1][0], list) and isinstance(row[1][0][0][0], bytes):
                    list_unique.append(row[1][0][0][0])
                elif isinstance(row[1][0], tuple) and isinstance(row[1][0][0], bytes):
                    list_unique.append(row[1][0][0])
                elif isinstance(row[1][0], bytes):
                    list_unique.append(row[1][0])

            len_set = len(set(list_unique))
            len_list = len(list_unique)
            if len_set != len_list:
                raise ValueError("!! Error: Generating list is not unique: {0} vs {1}".format(len_set, len_list))

        self.__post_parse_init()

        return self.__len_list_protocol

    def __post_parse_init(self):
        self.__len_list_protocol = len(self.__lists_protocol)
        self.__len_list_emit_send[CH_ESTRIGGER_CON] = len(self.__list_emit_send[CH_ESTRIGGER_CON][0])
        self.__len_list_emit_send[CH_ESTRIGGER_TIMEOUT] = len(self.__list_emit_send[CH_ESTRIGGER_TIMEOUT][0])

        tm = time.time()
        for i in range(self.__len_list_emit_send[CH_ESTRIGGER_TIMEOUT]):
            self.__list_emit_send[CH_ESTRIGGER_TIMEOUT][1].append(tm)

    def __generate_list_response(self, handler_dict_response, order, response, param_info):
        list_resp = []
        if isinstance(handler_dict_response, dict):
            func_handler_response = load_handler(**handler_dict_response)
            if order == CH_ORDER_GENERATOR:
                if isinstance(func_handler_response, list):
                    return func_handler_response, response
                else:
                    return [func_handler_response], response
            elif order == CH_ORDER_ZIP or order == CH_ORDER_SEMIDUPLEX:
                return self.__genearate_list_packet(handler_dict_response, response, param_info)
        elif isinstance(response, list):
            for resp in response:
                list_resp.append(str_hex2byte(resp))
        else:
            list_resp.append(str_hex2byte(response))
        return list_resp

    def __genearate_list_packet(self, handler_func_dict, data_packet, param_info):
        list_packet = []
        doc, order, index = param_info
        if isinstance(handler_func_dict, dict):
            func_handler = load_handler(self.config_vars, **handler_func_dict)
            try:
                for func in func_handler:
                    if data_packet is None:
                        res = func()
                    else:
                        res = func(data_packet)
                    if res:
                        list_packet.extend(res)
            except TypeError as e:
                raise TypeError("Wrong defined type order interaction: doc={0}, order={1}, index = {2}, {3}".format(
                    doc, order, index, e.args))
        elif isinstance(data_packet, list):
            for req in data_packet:
                list_packet.append(str_hex2byte(req))
        elif isinstance(data_packet, str):
            list_packet.append(str_hex2byte(data_packet))
        elif order == CH_ORDER_ZIP:
            raise ValueError(
                '!ERROR: not defined keyword "handler_request" for order = "{}": doc={}, data={}, index = {}'.format(
                    CH_ORDER_ZIP, doc, data_packet, index))

        else:
            raise ValueError(
                '!Error: invalid type "req/resp" data for parsing (str, list, dict): doc={}, data={}, order={}, index ={}'.format(
                    doc, data_packet, order, index))
        return list_packet

    def __process_generation_reponse(self, param_data, param_info):
        list_generator_resp, response, list_req, bytes_recv = param_data
        doc, order = param_info
        for generator_resp in list_generator_resp:
            if hasattr(generator_resp, '__call__'):  # it responses function-generator
                len_list_req = len(list_req)
                while self.__count_req_generator_packet < len_list_req:
                    packet_response = list_req[self.__count_req_generator_packet]
                    if packet_response[0] == bytes_recv:
                        if response is None:
                            write_data = generator_resp(packet_response)
                        else:
                            write_data = generator_resp(packet_response, response)

                        self.log.warning(u'!WARNING Handling command: "{0}", function = "{2}", order = {1}; '
                                         u'packet count = {3} of {4}'.format(doc, order, generator_resp.__name__,
                                                                             self.__count_req_generator_packet + 1,
                                                                             len_list_req))
                        self.__count_req_generator_packet = self.__increment_counter(self.__count_req_generator_packet,
                                                                                     len_list_req)
                        if write_data is not None:
                            return [write_data]
                        else:
                            raise ValueError(
                                "!Error at time processing generation response: {}".format(
                                    generator_resp.__name__))
                    if self.__count_req_generator_packet > 0:
                        self.log.error(
                            u'!ERROR: Divergence protocol command\'s: command="{0}",'
                            u'line_packet="{1}", function="{2}"'.format(
                                doc, self.__count_req_generator_packet + 1, generator_resp))
                        self.__count_req_generator_packet = 0
                    return None

                return None

    def __process_zip_response(self, param_data, param_info):
        list_resp, list_req, bytes_recv = param_data
        doc, order = param_info
        len_list_req = len(list_req)
        while self.__count_req_zip_packet < len_list_req:
            packet_request = list_req[self.__count_req_zip_packet]
            if packet_request == bytes_recv:
                write_data = list_resp[self.__count_req_zip_packet]

                self.log.info(u'!INFO: Handling command: "{0}", order = {1}; '
                              u'packet count = {2} of {3}'.format(doc, order, self.__count_req_zip_packet + 1,
                                                                  len_list_req))

                self.__count_req_zip_packet = self.__increment_counter(self.__count_req_zip_packet, len_list_req)

                if write_data is not None:
                    return [write_data]
                else:
                    raise ValueError(
                        "Error at time processing generation response: doc = {}".format(doc))
            if self.__count_req_zip_packet > 0:
                self.log.error(
                    u'!ERROR: Divergence protocol command\'s: command="{0}",'
                    u'line_packet="{1}"'.format(
                        doc, self.__count_req_zip_packet + 1))
                self.__count_req_zip_packet = 0
            return None
        return None

    def __process_semiduplex_response(self, param_data, param_info):
        list_resp, list_req, bytes_recv = param_data
        doc, order = param_info
        len_list_req = len(list_req)
        while self.__count_req_semiduplex_packet < len_list_req:
            packet_request = list_req[self.__count_req_semiduplex_packet]
            if packet_request == bytes_recv:
                write_data = list_resp[self.__count_req_semiduplex_packet]

                self.log.info(u'!INFO: Handling command: "{0}", order = {1}; '
                              u'packet count = {2} of {3}'.format(doc, order, self.__count_req_semiduplex_packet + 1,
                                                                  len_list_req))
                if write_data is not None:
                    if self.__count_req_semiduplex_packet == len_list_req - 1:
                        self.__count_req_semiduplex_packet = 0
                        self.__count_protocol = 0
                        return list_resp
                    else:
                        self.__count_req_semiduplex_packet += 1
                        return False
                else:
                    raise ValueError(
                        "Error at time processing generation response: doc = {}".format(doc))
            if self.__count_req_semiduplex_packet > 0:
                self.log.error(
                    u'!ERROR: Divergence protocol command\'s: command="{0}",'
                    u'line_packet="{1}"'.format(
                        doc, self.__count_req_semiduplex_packet + 1))
                self.__count_req_semiduplex_packet = 0
            return None
        return None

    def __increment_counter(self, value, len_list):
        if value == len_list - 1:
            value = 0
            self.__count_protocol = 0
        else:
            value += 1
        return value

    def handler_response(self, bytes_recv) -> [bytes]:
        """

        :param bytes_recv: received bytes array
        :return: list of bytes for writing to serial port or None to send nothing
        :rtype: bytes
        """
        if len(self.__list_gen_full) > 0:
            result = self.__process_full_generate_response_with_parser(bytes_recv)[0]
            if result:
                return result

        if not self.__lists_protocol:
            self.log.error("Error: List protocol did not loaded. It is empty")
            return None

        while self.__count_protocol < self.__len_list_protocol:
            cmd = self.__lists_protocol[self.__count_protocol]
            order = cmd[0]
            list_req = cmd[1]
            doc = cmd[3]
            self.log.debug("***  seek ---- order = {}, doc = {}".format(order, doc))
            if order == "generator" and self.__count_req_generator_packet >= 0 and \
                            self.__count_req_zip_packet == 0 and self.__count_req_semiduplex_packet == 0:
                list_generator_resp, response = cmd[2]
                result = self.__process_generation_reponse((list_generator_resp, response, list_req, bytes_recv),
                                                           (doc, order))
                if result:
                    return result
            elif order == "zip" and self.__count_req_zip_packet >= 0 and \
                            self.__count_req_generator_packet == 0 and self.__count_req_semiduplex_packet == 0:
                list_resp = cmd[2]
                result = self.__process_zip_response((list_resp, list_req, bytes_recv), (doc, order))
                if result:
                    return result
            elif order == "semiduplex" and self.__count_req_semiduplex_packet >= 0 and \
                            self.__count_req_generator_packet == 0 and self.__count_req_zip_packet == 0:
                list_resp = cmd[2]
                result = self.__process_semiduplex_response((list_resp, list_req, bytes_recv), (doc, order))
                if result is not None:
                    return result

            if self.__count_protocol == self.__len_list_protocol - 1:
                if self.__count_req_semiduplex_packet == 0 and \
                                self.__count_req_generator_packet == 0 and self.__count_req_zip_packet == 0:
                    self.log.error(
                        "!! Not found command of packet: {}, "
                        "amount sought protocol command's = {} of {}".format(
                            str_hex2byte(bytes_recv), self.__count_protocol + 1, self.__len_list_protocol))
                self.__count_protocol = 0
                return None
            else:
                self.__count_protocol += 1
