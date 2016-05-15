#!/usr/bin/env python

import logging
import serial


class SerialPortSettings(object):
    def __init__(self, port_name='', baud_rate='', databits='', parity='',
                 stop_bits='', timeout=0, delay_response=0):
        self.log = logging.getLogger('SerialPortSettings')
        self.__serial_settings = dict(port_name=port_name, baud_rate=baud_rate,
                                      timeout=timeout, parity=parity, stop_bits=stop_bits,
                                      databits=databits, delay_response=delay_response)

    def get_dict(self):
        return self.__serial_settings

    def __str__(self):
        return "{0} (baud_rate={1}, databits={2}, parity={3}, stop_bits={4}, timeout={5}, delay_response={6})".format(
            self.port, self.baud_rate, self.databits, self.parity_str, self.stop_bits, self.timeout, self.delay_response
        )

    def __repr__(self):
        return "SerialPortSettings (port={0}, baud_rate={1}, databits={2}, " \
               "parity={3}, stop_bits={4}, timeout={5}, delay_response={6})".format(
               self.port, self.baud_rate, self.databits, self.parity_str, self.stop_bits, self.timeout, self.delay_response
        )

    @property
    def parity_str(self):
        if self.parity == serial.PARITY_NONE:
            return 'none'
        if self.parity == serial.PARITY_EVEN:
            return 'even'
        if self.parity == serial.PARITY_ODD:
            return 'odd'

    def parse(self, settings):
        if settings:
            for opts in settings:
                if opts in self.__serial_settings.keys():
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
                    self.log.warning("!WARNING: Serial setting '{}' is redundant".format(opts))

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
    def delay_response(self):
        return self.__serial_settings['delay_response']

    @delay_response.setter
    def delay_response(self, value):
        self.__serial_settings['delay_response'] = value

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
   pass