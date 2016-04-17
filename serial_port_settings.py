#!/usr/bin/env python

import logging
import serial
from ImitatorDevice.settings_protocol import SettingsProtocol


class SerialPortSettings(object):
    def __init__(self, port_name='COM1', baud_rate=9600, databits=8, parity='N',
                 stop_bits=1, timeout=0):
        self.log = logging.getLogger('SettingsProtocol')
        self.__serial_settings = dict(port_name=port_name, baud_rate=baud_rate,
                                      timeout=0, parity=parity, stop_bits=stop_bits,
                                      databits=databits)

    def get_dict(self):
        return self.__serial_settings

    def parse(self, settings):
        for opts in self.__serial_settings.keys():
            if opts in settings:
                if opts == 'parity':
                    if settings[opts].lower().strip() == 'none':
                        settings[opts] = serial.PARITY_NONE
                    elif settings[opts].lower().strip() == 'even':
                        settings[opts] = serial.PARITY_EVEN
                    elif settings[opts].lower().strip() == 'odd':
                        settings[opts] = serial.PARITY_ODD
                    else:
                        raise ValueError("Serial settings: invalid value parity: {}"
                                         " [none, even, odd]".format(settings[opts]))
                if opts == 'databits' and int(settings[opts]) not in (5, 6, 7, 8):
                    raise ValueError("Serial settings: invalid value databits:"
                                     " {} [{}]".format(settings[opts], (5, 6, 7, 8)))
                if opts == 'stop_bits' and int(settings[opts]) not in (1, 1.5, 2):
                    raise ValueError("Serial settings: invalid value stop bits:"
                                     " {} [{}]".format(settings[opts], (1, 1.5, 2)))

                self.__serial_settings[opts] = settings[opts]
            else:
                self.log.warning("!WARNING: Serial settings is redundant")

    @property
    def port(self):
        return self.__serial_settings['port_name']

    @port.setter
    def port(self, value):
        self.__serial_settings['port_name'] = value

    @property
    def baud_rate(self):
        return self.__serial_settings['baud_rate']

    @baud_rate.setter
    def baud_rate(self, value):
        self.__serial_settings['baud_rate'] = value

    @property
    def databits(self):
        return self.__serial_settings['databits']

    @databits.setter
    def databits(self, value):
        self.__serial_settings['databits'] = value

    @property
    def stop_bits(self):
        return self.__serial_settings['stop_bits']

    @stop_bits.setter
    def stop_bits(self, value):
        self.__serial_settings['stop_bits'] = value

    @property
    def parity(self):
        return self.__serial_settings['parity']

    @parity.setter
    def parity(self, value):
        self.__serial_settings['parity'] = value

    @property
    def timeout(self):
        return self.__serial_settings['timeout']

    @timeout.setter
    def timeout(self, value):
        self.__serial_settings['timeout'] = value


if __name__ == '__main__':
    settings = SettingsProtocol(SerialPortSettings())
    settings.parse('protocol_serial_device.conf')
    print(settings.port_settings)
    print(settings.handler_response(b'\xa5\x00\x1b\x04\x01\x00\xff\x07\xe6\x17'))
    assert settings.handler_response(
        b'\xa5\x00\x1b\x04\x01\x00\xff\x07\xe6\x17') == b'\xa5\x00\x1f\x04\x00\x00\x00\x00\x1b\x17'
    assert settings.handler_response(
        b'\xa5\x00\x1b\x04\x00\x00\x00\x00\x1f\x17') == b'\xa5\x00\x1f\x04\x00\x00\x00\x00\x1b\x17'
