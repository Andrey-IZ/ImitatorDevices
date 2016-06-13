#!/usr/bin/env python
# -*- coding=utf-8 -*-

import serial
from ImitatorDevice.server_device_imitator import ThreadServerDeviceImitator
from tools_binary import byte2hex_str


class SerialOpenPortException(serial.SerialException):
    pass


class SerialDeviceException(Exception):
    pass


class ServerSerialDeviceimitator(ThreadServerDeviceImitator):
    """
    """

    def __init__(self, settings_conf, logger, control_gui=None):
        super(ServerSerialDeviceimitator, self).__init__(logger)
        self.serial = serial.Serial()
        self.__control_gui = control_gui
        self.handler_response = settings_conf.handler_response
        self.serial_settings = settings_conf.serialport_settings
        self.__init_serial(self.serial_settings)

    def __init_serial(self, port_settings):
        if self.serial_settings.port == '':
            return
        try:
            self.serial.port = port_settings.port  # , do_not_open=True)
            self.serial.timeout = 0  # required so that the reader thread can exit
            self.serial.baudrate = port_settings.baud_rate
            self.serial.parity = port_settings.parity
            self.serial.stopbits = port_settings.stop_bits
            self.serial.bytesize = port_settings.databits
        except Exception as err:
            exc_str = "!Error: Invalid class port settings: {}".format(port_settings)
            self.log.error(exc_str)
            raise SerialOpenPortException(exc_str) from err

    def __str__(self):
        return 'ServerSerialDeviceimitator(status={}, settings={})'.format(self.running,
                                                                           self.serial_settings.__repr__())

    def open_port(self, port_settings):
        try:
            self.__init_serial(port_settings)
            self.serial.open()
        except serial.SerialException as err:
            exc_str = "!ERROR:  Could not open serial port {}: {}".format(self.serial.name, err.args)
            self.log.error(exc_str)
            raise SerialOpenPortException(exc_str) from err
        return True

    def open(self):
        return self.open_port(self.serial_settings)

    def listen_port(self, port_settings, thread_name='serial-reader'):
        if self.open_port(port_settings):
            if hasattr(self.serial, 'is_open'):
                if self.serial.is_open:
                    super(ServerSerialDeviceimitator, self).listen(thread_name=self.serial.port)
                    return True
            elif hasattr(self.serial, 'isOpen'):
                if self.serial.isOpen:
                    super(ServerSerialDeviceimitator, self).listen(thread_name=self.serial.port)
                return True
        return False

    def listen(self, thread_name='serial-reader'):
        return self.listen_port(self.serial_settings, thread_name)

    def reader(self):
        """loop forever and handling packets protocol"""
        try:
            while self.running:
                data_recv = self.serial.read(self.serial.inWaiting())
                if data_recv:
                    self.log.warning("======================================")
                    self.log.warning("-> recv: {}".format((byte2hex_str(data_recv))))

                    if self.dict_values_form:
                        list_packets = self.handler_response(self.log, data_recv, self.dict_values_form)
                    else:
                        list_packets = self.handler_response(self.log, data_recv)
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


def serial_server_start(settings_conf, logger, control_gui):
    is_serial_server_start = False
    serial_server = None
    try:
        serial_server = ServerSerialDeviceimitator(settings_conf, logger, control_gui)
        logger.info("Serving serial port: {}".format(settings_conf.serialport_settings))
        is_serial_server_start = serial_server.listen()
    except SerialOpenPortException as e:
        logger.error("Error for opening serial port {0}: {1}".format(serial_server.serial_settings, e.args))
    except Exception as e:
        logger.error("Error by starting serial server listen: {0}".format(e.args))
    finally:
        if serial_server and not is_serial_server_start:
            serial_server.stop()
            serial_server = None
            logger.info('Disconnected serial interface: {}'.format(serial_server))
    return serial_server
