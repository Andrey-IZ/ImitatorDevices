#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import sys

from ImitatorDevice.protocol.handling_protocol import HandlingProtocol
from ImitatorDevice.serial.ServerSerialDeviceImitator import *
from ImitatorDevice.socket.ServerSocketDeviceImitator import *
from imitator_serial_device_params import ImitatorSerialDeviceParams
import handlers_ukcu


def serial_server_start():
    is_serial_server_start = False
    serial_server = None
    try:
        serial_server = ServerSerialDeviceimitator(settings_conf)
        serial_server.open_port()
        logging.info("Serving serial port: {}".format(settings_conf.serialport_settings))
        is_serial_server_start = serial_server.listen()
    except SerialOpenPortException as e:
        pass
    except Exception:
        pass
    finally:
        if serial_server and not is_serial_server_start:
            serial_server.stop()
            serial_server = None
            logging.info('Disconnected serial interface: {}'.format(serial_server))
    return serial_server


def socket_server_start():
    is_socket_server_start = False
    socket_server = None
    try:
        socket_server = ServerSocketDeviceimitator(settings_conf)
        socket_server.open_port()
        logging.info("Serving socket port: {}".format(settings_conf.socket_settings))
        is_socket_server_start = socket_server.listen()
    except SocketBindPortException:
        pass
    except Exception:
        raise SocketDeviceException()
    finally:
        if socket_server and not is_socket_server_start:
            socket_server.stop()
            socket_server = None
            logging.info('Disconnected socket interface: {}'.format(socket_server))
    return socket_server

if __name__ == '__main__':

    params = ImitatorSerialDeviceParams(path_to_conf='protocol_serial_device.conf')
    params.parse_args()

    file_conf = params.path_to_conf
    logging.basicConfig(format=u'%(asctime)-15s [%(threadName)s] %(message)s',
                        level=params.level)
    logging.info("Level output messages set to " + params.level_str)

    cmd = ''

    while True:

        settings_conf = HandlingProtocol()
        logging.info("Parsing configuration file: {}".format(file_conf))
        settings_conf.parse(file_conf)
        logging.info("Imitator serial devices start")
        print(
            u">>> Imitator serial device is started.  Enter 'exit' or Ctrl+C enter for quit. "
            u"Enter 'start' to start server")
        try:
            try:
                serial_server = serial_server_start()
                socket_server = socket_server_start()

                if not serial_server and not socket_server:
                    print(u">>> Imitator device was stop")
                    break
                while True:
                    cmd = input()
                    if cmd == 'stop' or cmd == 'exit' or cmd == 'restart':
                        str_info = '>> Imitator device is ' + cmd + 'ed'
                        logging.debug(str_info)
                        print(str_info)
                        break

            except SerialDeviceException as err:
                logging.error("!Error: occurrence with serial port server: {}".format(err))
                sys.stdout.write('\n')
                break
            finally:
                if serial_server:
                    serial_server.stop()
                if socket_server:
                    socket_server.stop()
                logging.info('Disconnected all interfaces')
            if cmd == 'exit':
                break

            while True:
                if cmd == 'restart':
                    logging.warning('***************************************')
                    break
                cmd = input(">>> Enter 'start' to start server: ")
                if cmd == 'start':
                    logging.warning('***************************************')
                    break
                if cmd != 'exit':
                    continue
                break
            break
        except KeyboardInterrupt:
            sys.stdout.write('\n')
    logging.info('--- exit ---')
