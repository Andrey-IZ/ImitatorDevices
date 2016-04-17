#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import serial
import sys
from imitator_serial_device import SettingsProtocol, SerialServer


if __name__ == '__main__':
    logging.basicConfig(format=u'%(asctime)-15s [%(threadName)s] %(message)s',
                        level=logging.INFO)
    file_conf = 'protocol_serial_device.conf'
    settings_conf = SettingsProtocol()
    logging.info("Parsing configuration file: {}".format(file_conf))
    settings_conf.parse(file_conf)
    logging.info("Imitator serial devices start")

    # connect to serial port
    ser = serial.Serial()
    ser.port = settings_conf.serial_settings.get('port_name')#, do_not_open=True)
    ser.timeout = 3     # required so that the reader thread can exit
    ser.baudrate = settings_conf.serial_settings.get('baud_rate')
    ser.parity = settings_conf.serial_settings.get('parity')
    ser.stopbits = settings_conf.serial_settings.get('stop_bits')
    ser.bytesize = settings_conf.serial_settings.get('databits')

    # reset control line as no _remote_ "terminal" has been connected yet
    # ser.dtr = False
    # ser.rts = False

    try:
        ser.open()
    except serial.SerialException as e:
        logging.error("!ERROR:  Could not open serial port {}: {}".format(ser.name, e))
        sys.exit(1)

    cmd = ''
    serial_settings = ser.getSettingsDict()

    while True:
        print(u">>> Imitator serial device is started.  Enter 'exit' for quit. Enter 'start' to start server")
        try:
            logging.info("Serving serial port: {}".format(settings_conf.serial_settings))
            # ser.rts = True
            # ser.dtr = True
            serial_server = SerialServer(ser, settings_conf)
            try:
                serial_server.listen()
                while True:
                    cmd = input()
                    if cmd == 'stop' or cmd == 'exit':
                        break
            finally:
                logging.info('Disconnected')
                serial_server.stop()
                # ser.dtr = False
                # ser.rts = False
                # Restore port settings (may have been changed by RFC 2217
                # capable client)
                ser.apply_settings(serial_settings)
                print(u">>> Imitator serial device was stop")
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