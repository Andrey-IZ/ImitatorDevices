#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import sys

from ImitatorDevice.protocol.handling_protocol import HandlingProtocol
from ImitatorDevice.serial.ServerSerialDeviceImitator import *
from imitator_serial_device import ImitatorSerialDeviceParams

if __name__ == '__main__':

    params = ImitatorSerialDeviceParams(path_to_conf='protocol_serial_device.conf')
    params.parse_args()

    file_conf = params.path_to_conf
    logging.basicConfig(format=u'%(asctime)-15s [%(threadName)s] %(message)s',
                        level=params.level)
    logging.info("Level output messages set to " + params.level_str)
    settings_conf = HandlingProtocol(SerialPortSettings())
    logging.info("Parsing configuration file: {}".format(file_conf))
    settings_conf.parse(file_conf)
    logging.info("Imitator serial devices start")
    #
    # # connect to serial port
    # ser = serial.Serial()
    # ser.port = settings_conf.port_settings.port  # , do_not_open=True)
    # ser.timeout = 3  # required so that the reader thread can exit
    # ser.in_baudrate = settings_conf.port_settings.baud_rate
    # ser.parity = settings_conf.port_settings.parity
    # ser.stopbits = settings_conf.port_settings.stop_bits
    # ser.bytesize = settings_conf.port_settings.databits

    cmd = ''

    while True:
        print(
            u">>> Imitator serial device is started.  Enter 'exit' or Ctrl+C enter for quit. "
            u"Enter 'start' to start server")
        try:
            logging.info("Serving serial port: {}".format(settings_conf.port_settings))
            serial_server = ServerSerialDeviceimitator(settings_conf.handler_response, settings_conf.port_settings)
            try:
                serial_server.open_port()
            except SerialOpenPortException as e:
                print('Press <Enter> for exit from application\n')
                sys.exit(1)
            try:
                serial_server.listen()
                while True:
                    cmd = input()
                    if cmd == 'stop' or cmd == 'exit':
                        break
            finally:
                logging.info('Disconnected')
                serial_server.stop()
                print(u">>> Imitator device was stop")
        except KeyboardInterrupt:
            sys.stdout.write('\n')
            break
        except SerialDeviceException as err:
            logging.error("!Error: occurrence with serial port server: {}".format(err))
            sys.stdout.write('\n')
            break
        if cmd == 'exit':
            break

        while True:
            cmd = input()
            if cmd == 'start':
                break

    logging.info('--- exit ---')
