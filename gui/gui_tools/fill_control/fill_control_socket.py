import socket
import sys
import glob
import json


class SocketOpenPortException(socket.error):
    pass


FC_SOCKET_CMB_PORT, FC_SOCKET_CMB_ADDRESS = ('port_cmb', 'address_cmb')


class FillControlSocket(object):
    def __init__(self, log, settings_socket):
        self.socket = None
        self.__settings_default = {FC_SOCKET_CMB_PORT: '127.0.0.1',
                                   FC_SOCKET_CMB_ADDRESS: 11000}
        self.log = log
        self.__port = self.__settings_default[FC_SOCKET_CMB_PORT]
        self.__address = self.__settings_default[FC_SOCKET_CMB_ADDRESS]
        self.settings = self.__load_socket_settings(settings_socket)

    @property
    def port(self):
        return self.__port

    @property
    def address(self):
        return self.__address

    def __load_socket_settings(self, set_sc):
        try:
            if set_sc:
                settings = dict()
                settings[FC_SOCKET_CMB_PORT] = set_sc.port if set_sc else self.__settings_default[FC_SOCKET_CMB_PORT]
                host = '127.0.0.1' if set_sc.host == 'localhost' else set_sc.host
                settings[FC_SOCKET_CMB_ADDRESS] = host if host else self.__settings_default[FC_SOCKET_CMB_PORT]
                return settings
        except Exception:
            print('!INFO: Not loaded settings')
        return self.__settings_default

    def init_controls(self, port_sb, address_ledit):
        try:
            port_sb.setValue(self.settings[FC_SOCKET_CMB_PORT])
            address_ledit.setText(self.settings[FC_SOCKET_CMB_ADDRESS])
        except Exception:
            self.log.info('!INFO: Did not load file settings for sockets')

    # def __init_socket(self, **serial_settings):
    #     self.socket = serial.Serial()
    #     if not serial_settings.get('port'):
    #         return None
    #     try:
    #         self.serial.port = serial_settings.get('port')  # , do_not_open=True)
    #         self.serial.timeout = 0  # required so that the reader thread can exit
    #         self.serial.baudrate = serial_settings.get('baud_rate')
    #         self.serial.parity = self.__get_parity(serial_settings.get('parity'))
    #         self.serial.stopbits = self.__get_stop_bits(serial_settings.get('stop_bits'))
    #         self.serial.bytesize = self.__get_databits(serial_settings.get('databits'))
    #     except Exception as err:
    #         exc_str = "!ERROR: Invalid class port settings: {}".format(serial_settings)
    #         raise SerialOpenPortException(exc_str) from err
    #     return True

    # def __open_port(self):
    #     try:
    #         self.serial.open()
    #     except serial.SerialException as err:
    #         exc_str = "!ERROR:  Could not open serial port {}: {}".format(self.serial.name, err.args)
    #         raise SerialOpenPortException(exc_str) from err
    #     return True
