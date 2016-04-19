#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import serial
import sys
from serial_port_settings import SettingsProtocol, SerialPortSettings
from imitator_serial_device import ImitatorSerialDeviceParams
from ImitatorDevice.server_device_imitator import ServerDeviceImitator
import handlers_ukcu

if __name__ == '__main__':

    params = ImitatorSerialDeviceParams(path_to_conf='protocol_serial_device.conf')
    params.parse_args()

    file_conf = params.path_to_conf
    logging.basicConfig(format=u'%(asctime)-15s [%(threadName)s] %(message)s',
                        level=params.level)
    logging.info("Level output messages set to " + params.level_str)
    settings_conf = SettingsProtocol(SerialPortSettings())
    logging.info("Parsing configuration file: {}".format(file_conf))
    settings_conf.parse(file_conf)
    logging.info("Imitator serial devices start")

    # connect to serial port
    ser = serial.Serial()
    ser.port = settings_conf.port_settings.port  # , do_not_open=True)
    ser.timeout = 3  # required so that the reader thread can exit
    ser.in_baudrate = settings_conf.port_settings.baud_rate
    ser.parity = settings_conf.port_settings.parity
    ser.stopbits = settings_conf.port_settings.stop_bits
    ser.bytesize = settings_conf.port_settings.databits

    try:
        ser.open()
    except serial.SerialException as e:
        logging.error("!ERROR:  Could not open serial port {}: {}".format(ser.name, e))
        input('For exit from application push <Enter>\n')
        sys.exit(1)

    cmd = ''

    while True:
        print(
            u">>> Imitator serial device is started.  Enter 'exit' or Ctrl+C enter for quit. "
            u"Enter 'start' to start server")
        try:
            logging.info("Serving serial port: {}".format(settings_conf.port_settings))
            serial_server = ServerDeviceImitator(settings_conf, ser.write, ser.read, (ser.inWaiting, 'call'))
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

        if cmd == 'exit':
            break

        while True:
            cmd = input()
            if cmd == 'start':
                break

    logging.info('--- exit ---')
