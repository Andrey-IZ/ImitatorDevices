#!/usr/bin/env python
# -*- coding=utf-8 -*-

import serial
from ImitatorDevice.server_device_imitator import ServerDeviceImitator
from tools_binary import byte2hex_str


class SerialOpenPortException(serial.SerialException):
    pass


class SerialDeviceException(Exception):
    pass


class ServerSerialDeviceimitator(ServerDeviceImitator):
    """
    """

    def __init__(self, settings_conf):
        super().__init__('Serial Server')
        self.serial = None
        self.handler_response = settings_conf.handler_response
        self.port_settings = settings_conf.serialport_settings
        self.__init_serial()

    def __init_serial(self):
        self.serial = serial.Serial()
        try:
            self.serial.port = self.port_settings.port  # , do_not_open=True)
            self.serial.timeout = 0  # required so that the reader thread can exit
            self.serial.in_baudrate = self.port_settings.baud_rate
            self.serial.parity = self.port_settings.parity
            self.serial.stopbits = self.port_settings.stop_bits
            self.serial.bytesize = self.port_settings.databits
        except Exception as err:
            exc_str = "!Error: Invalid class port settings: {}".format(self.port_settings)
            self.log.error(exc_str)
            raise SerialOpenPortException(exc_str) from err

    def open_port(self):
        try:
            self.serial.open()
        except serial.SerialException as err:
            exc_str = "!ERROR:  Could not open serial port {}: {}".format(self.serial.name, err.args)
            self.log.error(exc_str)
            raise SerialOpenPortException(exc_str) from err
        return True

    def listen(self, thread_name='serial-reader'):
        if hasattr(self.serial, 'is_open'):
            if self.serial.is_open:
                super().listen(thread_name=self.serial.port)
                return True
        elif hasattr(self.serial, 'isOpen'):
            if self.serial.isOpen:
                super().listen(thread_name=self.serial.port)
            return True
        return False

    def reader(self):
        """loop forever and handling packets protocol"""
        try:
            while self.alive:
                data_recv = self.serial.read(self.serial.inWaiting())
                if data_recv:
                    self.log.warning("======================================")
                    self.log.warning("-> recv: {}".format((byte2hex_str(data_recv))))

                    list_packets = self.handler_response(data_recv)
                    if list_packets:
                        for packet in list_packets:
                            if packet:
                                self.log.warning("<- send: {}".format(byte2hex_str(packet)))
                                self.serial.write(packet)
        except serial.SerialException as err:
            exc_str = "!ERROR: Occurrence for read/write to serial port"
            self.log.error(exc_str)
            raise SerialDeviceException(exc_str) from err
        except ValueError as err:
            exc_str = "!ERROR: Occurrence into handlers for process packets"
            self.log.error(exc_str)
            raise SerialDeviceException(exc_str) from err
        except Exception as err:
            exc_str = "!ERROR: Occurrence unknown mistake  at time process packets"
            self.log.error(exc_str)
            raise SerialDeviceException(exc_str) from err
        finally:
            self.serial.close()
