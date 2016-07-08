#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
from ImitatorDevice.protocol.handling_protocol import HandlingProtocol
from imitator_serial_socket_device_params import ImitatorSeriaSocketlDeviceParams
import sys
import os.path
from cli.main_cli import start_server_cli
from gui.main_gui import start_server_gui
from gui.qt_logging import QtHandler
from libs.log_tools.logger import Logger
from ImitatorDevice.protocol.handling_protocol import GuiUsedException


def init_logging(params):
    logger = Logger('ImDev')
    log_formatter = logging.Formatter(u'%(asctime)-15s <%(levelname)-1.1s> [%(name)s~%(qthreadName)s] %(message)s')
    logger.setLevel(params.level)

    if params.logfile_path:
        fileHandler = logging.FileHandler(params.logfile_path, encoding='utf-8')
        fileHandler.setFormatter(log_formatter)
        logger.addHandler(fileHandler)

    if params.interface == 'gui':
        gui_handler = QtHandler()
        gui_handler.setFormatter(log_formatter)
        logger.addHandler(gui_handler)
    # elif params.interface == 'cli':
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(log_formatter)
    logger.addHandler(console_handler)
    return logger


if __name__ == '__main__':
    params = ImitatorSeriaSocketlDeviceParams()
    params.parse_args()

    logger = init_logging(params)

    logger.info("--- Start application ---")
    logger.info("Level output messages set to " + params.level_str)

    file_conf = params.path_to_conf
    if not os.path.exists(file_conf):
        logger.error('!Error: configuration file "{}" not found'.format(file_conf))
        sys.exit(1)

    cmd = ''
    settings_conf = HandlingProtocol(logger)
    if params.interface == 'cli':
        start_server_cli(logger, params, settings_conf, file_conf)
    elif params.interface == 'gui':
        start_server_gui(logger, params, settings_conf, file_conf)
