#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import sys
from ImitatorDevice.protocol.handling_protocol import HandlingProtocol
from ImitatorDevice.serial.ServerSerialDeviceImitator import *
from ImitatorDevice.socket.ServerSocketDeviceImitator import *
from imitator_serial_socket_device_params import ImitatorSeriaSocketlDeviceParams
import handlers_ukcu


def serial_server_start(settings_conf):
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


def socket_server_start(settings_conf):
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

    params = ImitatorSeriaSocketlDeviceParams(path_to_conf='protocol_serial_device.conf')
    params.parse_args()

    file_conf = params.path_to_conf
    logging.basicConfig(format=u'%(asctime)-15s [%(threadName)s] %(message)s',
                        level=params.level)
    logging.info("Level output messages set to " + params.level_str)

    cmd = ''
    settings_conf = HandlingProtocol()

    if params.run_serial or params.run_socket:
        print(params)
        while True:
            logging.warning("Imitator serial devices started")
            print(
                u">>> Enter 'exit' or Ctrl+C enter for quit. "
                u"Enter 'start' to start server. \n>>> Enter 'restart' for restart servers. ")
            print(u">>> Enter 'reconf' for reload configuration file without restart of servers")

            logging.info("Parsing configuration file: {}".format(file_conf))
            try:
                settings_conf.parse(file_conf)
            except ImportError as err:
                logging.error(err)


            serial_server = None
            socket_server = None
            try:
                try:
                    if params.run_serial:
                        serial_server = serial_server_start(settings_conf)
                    if params.run_socket:
                        socket_server = socket_server_start(settings_conf)

                    if not serial_server and not socket_server:
                        print(u">>> Imitator device was stop")
                        break
                    while True:
                        cmd = input()
                        if cmd == 'stop' or cmd == 'exit' or cmd == 'restart':
                            str_info = '>> Imitator device is ' + cmd + 'ed'
                            logging.warning(str_info)
                            print(str_info)
                            break
                        elif cmd == 'reconf':
                            settings_conf.parse(params.path_to_conf)
                            logging.warning('File configuration: {} was reload'.format(params.path_to_conf))

                except SerialDeviceException as err:
                    logging.error("!Error: occurrence with serial port server: {}".format(err))
                    sys.stdout.write('\n')
                    raise KeyboardInterrupt()

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
                    if cmd == 'exit':
                        raise KeyboardInterrupt()
                    break
            except KeyboardInterrupt:
                pass
            except EOFError:
                pass
            finally:
                try: serial_server.stop()
                except: pass
                try: socket_server.stop()
                except: pass
                logging.warning('Disconnected all interfaces')
                break
    else:
        logging.error("!Error: Not defined start interface !")
    logging.info('--- exit ---')
