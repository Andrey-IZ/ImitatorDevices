#!/usr/bin/env python

import logging

from ImitatorDevice.tools_parse_yaml_protocol import str_hex2byte, load_handler, \
    load_conf_test, str_dict_keys_lower


class SettingsProtocol(object):
    """
    It implements  parsing and algorithmic handling loaded protocol configuration
    """

    def __init__(self, port_settings):
        self.__port_settings = port_settings
        self.log = logging.getLogger('SettingsProtocol')
        self.__lists_protocol = []
        self.__count_req_generator_packet = 0
        self.__count_req_zip_packet = 0
        self.__count_req_semiduplex_packet = 0
        self.__count_protocol = 0
        self.__len_list_porotocol = 0
        self.__is_processing_resp = False

    @property
    def port_settings(self):
        """

        :return: dictionary interface, generating from class PortSettings
        """
        return self.__port_settings

    @port_settings.setter
    def port_settings(self, value):
        """

        :param value: dictionary interface, generating from class PortSettings
        :return:
        """
        self.__port_settings = value

    def parse(self, file_name):
        """
        It makes parsing file_name and generates lists of protocol
        :param file_name:
        :return:
        """
        conf = load_conf_test(file_name)
        self.port_settings.parse(conf[:1][0])

        self.__lists_protocol.clear()
        for i, cmd in enumerate(conf[1:]):
            cmd = str_dict_keys_lower(cmd)
            doc = cmd.get('doc')
            if not isinstance(doc, str) and not doc:
                raise ValueError(
                    u"Parse error: in conf didn't find parameter doc or it is empty: command = {}".format(i))
            doc = doc.strip()
            request = cmd.get('request')
            response = cmd.get('response')

            order = cmd.get('order', 'zip').lower()
            handler_response = cmd.get('handler_response')
            handler_request = cmd.get('handler_request')

            list_req = self.__genearate_list_packet(handler_request, request, (doc, order))
            if len(list_req) == 0:
                raise ValueError("Parse error: packet loaded nothing for: {0}".format(doc))

            gen_list_resp = self.__generate_list_response(handler_response, order, response, (doc, order))
            if order != 'semiduplex' and isinstance(gen_list_resp, list) and len(list_req) != len(gen_list_resp):
                raise ValueError("!! Error: Generating lists for responses and requests is not equal: "
                                 "{0} vs {1}, doc = '{2}', order = {3}".format(len(gen_list_resp), len(list_req), doc,
                                                                               order))
            self.__lists_protocol.append((order, list_req, gen_list_resp, doc))

        if isinstance(self.__lists_protocol[0], tuple) and len(self.__lists_protocol) > 0:
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
        self.__len_list_porotocol = len(self.__lists_protocol)
        return self.__len_list_porotocol

    @staticmethod
    def __generate_list_response(handler_dict_response, order, response, param_info):
        list_resp = []
        if isinstance(handler_dict_response, dict):
            func_handler_response = load_handler(**handler_dict_response)
            if order == 'generator':
                if isinstance(func_handler_response, list):
                    return func_handler_response, response
                else:
                    return [func_handler_response], response
            elif order == 'zip' or order == 'semiduplex':
                return SettingsProtocol.__genearate_list_packet(handler_dict_response, response, param_info)
        elif isinstance(response, list):
            for resp in response:
                list_resp.append(str_hex2byte(resp))
        else:
            list_resp.append(str_hex2byte(response))
        return list_resp

    @staticmethod
    def __genearate_list_packet(handler_func_dict, data_packet, param_info):
        list_packet = []
        if isinstance(handler_func_dict, dict):
            func_handler = load_handler(**handler_func_dict)
            try:
                for func in func_handler:
                    if data_packet is None:
                        list_packet.extend(func())
                    else:
                        list_packet.extend(func(data_packet))
            except TypeError as e:
                doc, order = param_info
                raise TypeError(
                    "Wrong defined type order interaction: doc={0}, order={1}, {2}".format(doc, order, e.args))
        elif isinstance(data_packet, list):
            for req in data_packet:
                list_packet.append(str_hex2byte(req))
        else:
            list_packet.append(str_hex2byte(data_packet))
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

                        self.log.info(u'!INFO: Handling command: "{0}", function = "{2}", order = {1}; '
                                      u'packet count = {3} of {4}'.format(doc, order, generator_resp.__name__,
                                                                          self.__count_req_generator_packet + 1,
                                                                          len_list_req))
                        self.__count_req_generator_packet = self.__increment_counter(self.__count_req_generator_packet,
                                                                                     len_list_req)
                        if write_data is not None:
                            return [write_data]
                        else:
                            raise ValueError(
                                "Error at time processing generation response: {}".format(
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

    def handler_response(self, bytes_recv):
        """

        :param bytes_recv: received bytes array
        :return: list of bytes for writing to serial port or None to send nothing
        :rtype: bytes
        """
        if not self.__lists_protocol:
            raise ValueError("List protocol did not loaded. It is empty")
        while self.__count_protocol < self.__len_list_porotocol:
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

            if self.__count_protocol == self.__len_list_porotocol - 1:
                if self.__count_req_semiduplex_packet == 0 and \
                                self.__count_req_generator_packet == 0 and self.__count_req_zip_packet == 0:
                    self.log.error(
                        "!_WARNING_!: Not found command of packet: {}, "
                        "amount sought protocol command's = {} of {}".format(
                            str_hex2byte(bytes_recv), self.__count_protocol + 1, self.__len_list_porotocol))
                self.__count_protocol = 0
                return None
            else:
                self.__count_protocol += 1
