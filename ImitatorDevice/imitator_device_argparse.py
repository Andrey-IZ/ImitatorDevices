#!/usr/bin/env python
# -*- coding=utf-8 -*-

import sys
import logging
import argparse

__author__ = 'Andrey'


class ImitatorDeviceParams(object):
    def __init__(self, path_to_conf, level='DEBUG'):
        self._parser = argparse.ArgumentParser(prog=sys.argv[0], description='Using for debug client applications',
                                               formatter_class=argparse.ArgumentDefaultsHelpFormatter)
        self.__path_to_conf = path_to_conf
        self._choices = {'ERROR': logging.ERROR, 'INFO': logging.INFO, 'DEBUG': logging.DEBUG,
                         'WARNING': logging.WARNING}
        self.__level = level if level in self._choices else None
        self._args = None
        self._init_args()

    def __get_level_log(self):
        if self._args:
            return self._choices.get(self._args.level)
        else:
            return None

    def _init_args(self):
        self._parser.add_argument('-p', '--conf-path', dest='conf_path', help='Set path to configuration file',
                                  default=self.__path_to_conf)
        self._parser.add_argument('-l', '--level', dest='level', choices=sorted(self._choices.keys()),
                                  help='Set level output messages', default=self.__level)

    def parse_args(self):
        self._args = self._parser.parse_args()
        return self._args

    def __str__(self):
        if not self._args:
            return 'ImitatorDeviceParams(None)'
        param = 'ImitatorDeviceParams(path_to_conf={0}, level={1})'.format(
            self._args.conf_path, self._args.level)
        return param



    @property
    def level_str(self):
        if not self._args:
            return None
        return self._args.level

    @property
    def level(self):
        if not self._args:
            return None
        return self.__get_level_log()

    @property
    def path_to_conf(self):
        if not self._args:
            return None
        return self._args.conf_path
