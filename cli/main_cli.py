#!/usr/bin/env python
# -*- coding: utf-8 -*-


import copy
import sys

from imitator_device.interfaces.serial.ServerSerialDeviceImitator import serial_server_start, SerialDeviceException
from imitator_device.interfaces.socket.ServerSocketDeviceImitator import *
from imitator_device.protocol.handling_protocol import GuiUsedException


def start_server_cli(logger, params, settings_conf, file_conf):
    if params.run_serial or params.run_socket:
        while True:
            logger.critical("Imitator serial devices started")
            print(
                u">>> Enter 'exit' or Ctrl+C enter for quit. "
                u"Enter 'start' to start server. \n>>> Enter 'restart' for restart servers. ")
            print(u">>> Enter 'reconf' for reload configuration file without restart of servers")

            logger.critical("Parsing configuration file: {}".format(file_conf))
            try:
                stat = settings_conf.parse(file_conf)
                if params.is_show_stat:
                    logger.critical("Results parsing file {}:".format(file_conf) + stat)
            except GuiUsedException:
                raise GuiUsedException()
            except Exception as err:
                logger.error('>>> {}'.format(err))
                raise Exception(err) from err

            serial_server = None
            socket_server = None
            try:
                try:
                    if params.run_serial:
                        serial_logger = copy.copy(logger)
                        serial_logger.name = 'Serial'
                        serial_server = serial_server_start(settings_conf, serial_logger)
                    if params.run_socket:
                        socket_logger = copy.copy(logger)
                        socket_logger.name = 'Socket'
                        socket_server = socket_server_start(settings_conf, socket_logger)

                    if not serial_server and not socket_server:
                        print(u">>> Imitator device was stop")
                        break
                    while True:
                        cmd = input()
                        if cmd == 'stop' or cmd == 'exit' or cmd == 'restart':
                            str_info = '>>> Imitator device is ' + cmd + 'ed'
                            logger.warning(str_info)
                            print(str_info)
                            break
                        elif cmd == 'reconf':
                            settings_conf.parse(params.path_to_conf)
                            logger.critical('File configuration: {} was reload'.format(params.path_to_conf))

                except SerialDeviceException as err:
                    logger.error("!Error: occurrence with serial port server: {}".format(err))
                    sys.stdout.write('\n')
                    raise KeyboardInterrupt()

                if cmd == 'exit':
                    break

                while True:
                    if cmd == 'restart':
                        logger.warning('***************************************')
                        break
                    cmd = input(">>> Enter 'start' to start server: ")
                    if cmd == 'start':
                        logger.warning('***************************************')
                        break
                    if cmd == 'exit':
                        raise KeyboardInterrupt()
                continue
            except KeyboardInterrupt:
                print('KeyboardInterrupt')
                break
            except EOFError:
                break
            finally:
                try: serial_server.stop()
                except: pass
                try: socket_server.stop()
                except: pass
                logger.critical(' -- Disconnected all interfaces --')
    else:
        logger.error("!Error: Not defined start interface! Using option: '-c' or/and '-s' ")
    logger.critical('--- exit ---')
