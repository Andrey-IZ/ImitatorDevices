#!/usr/bin/env python

import logging
import socket


class SocketSettings(object):
    def __init__(self, port='', host='', socket_type='', timeout=0, delay_response=0):
        self.log = logging.getLogger('SocketSettings')
        self.__socket_settings = dict(port=port, host=host, delay_response=delay_response,
                                      timeout=timeout, socket_type=socket_type)

    def get_dict(self):
        return self.__socket_settings

    @property
    def socket_type_str(self):
        if self.socket_type == socket.SOCK_STREAM:
            return 'TCP'
        if self.socket_type == socket.SOCK_DGRAM:
            return 'UDP'

    def __str__(self):
        return "{1}:{0} (socket_type={2}, timeout={3}, delay_response={4})".format(
            self.port, self.host, self.socket_type_str, self.timeout, self.delay_response
        )

    def __repr__(self):
        return "SocketSettings (host={1}, socket_type={2}, timeout={3}, delay_response={4})".format(
               self.port, self.host, self.socket_type_str, self.timeout, self.delay_response
        )

    def parse(self, settings):
        if settings:
            for opts in settings:
                if opts in self.__socket_settings.keys():
                    if opts == 'socket_type':
                        if settings[opts].lower().strip() == 'tcp':
                            settings[opts] = socket.SOCK_STREAM
                        elif settings[opts].lower().strip() == 'udp':
                            settings[opts] = socket.SOCK_DGRAM
                        else:
                            raise ValueError("Socket settings: invalid value socket_type: {}"
                                             " [tcp, udp]".format(settings[opts]))

                    self.__socket_settings[opts] = settings[opts]
                else:
                    self.log.warning("!WARNING: Socket setting: '{}' is redundant".format(opts))

    @property
    def port(self):
        return self.__socket_settings['port']

    @port.setter
    def port(self, value):
        self.__socket_settings['port'] = value

    @property
    def host(self):
        return self.__socket_settings['host']

    @host.setter
    def host(self, value):
        self.__socket_settings['host'] = value

    @property
    def socket_type(self):
        return self.__socket_settings['socket_type']

    @socket_type.setter
    def socket_type(self, value):
        self.__socket_settings['socket_type'] = value

    @property
    def timeout(self):
        return self.__socket_settings['timeout']

    @timeout.setter
    def timeout(self, value):
        self.__socket_settings['timeout'] = value

    @property
    def delay_response(self):
        return self.__socket_settings['delay_response']

    @delay_response.setter
    def delay_response(self, value):
        self.__socket_settings['delay_response'] = value


if __name__ == '__main__':
   pass