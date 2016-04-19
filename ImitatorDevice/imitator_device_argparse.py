#!/usr/bin/env python
# -*- coding=utf-8 -*-

import logging
import argparse

__author__ = 'Andrey'


class ImitatorDeviceParams(object):
    def __init__(self, path_to_conf, level='DEBUG'):
        self.__parser = argparse.ArgumentParser(usage='Run %(prog) with specify values datas',
                                                formatter_class=argparse.ArgumentDefaultsHelpFormatter)
        self.__path_to_conf = path_to_conf
        self._choices = {'ERROR': logging.ERROR, 'INFO': logging.INFO, 'DEBUG': logging.DEBUG,
                         'WARNING': logging.WARNING}
        self.__level = level if level in self._choices else None
        self.__args = None
        self._init_args()

    def __get_level_log(self):
        return self._choices.get(self.__level)

    def _init_args(self):
        self.__parser.add_argument('--conf-path', dest='conf_path', help='Set path to configuration file',
                                   default=self.__path_to_conf)
        self.__parser.add_argument('--level', dest='level', choices=['INFO', 'DEBUG', 'WARNING'],
                                   help='Set level output messages')

    def parse_args(self):
        self.__args = self.__parser.parse_args()
        return self.__args

    def __str__(self):
        if not self.__args:
            return 'ImitatorDeviceParams(None)'
        param = 'ImitatorDeviceParams(path_to_conf={0}, level={1})'.format(
            self.__args.conf_path, self.__args.level)
        return param

    @property
    def level(self):
        if not self.__args:
            return None
        return self.__get_level_log()

    @property
    def path_to_conf(self):
        if not self.__args:
            return None
        return self.__args.conf_path
