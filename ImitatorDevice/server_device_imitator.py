#!/usr/bin/env python
# -*- coding=utf-8 -*-

import logging
import threading


class ServerDeviceImitator(object):
    def __init__(self, logger):
        self.log = logger
        self.thread_read = None
        self.alive = False
        self.thread_name = 'reader'

    def _reader(self):
        """loop forever and handling packets protocol"""
        self.log.warning('{} thread started'.format(self.thread_name))
        try:
            self.reader()
        finally:
            self.alive = False
            self.log.warning('{} thread terminated'.format(self.thread_name))

    def reader(self):
        pass

    def listen(self, thread_name=''):
        self.alive = True
        self.thread_read = threading.Thread(target=self._reader)
        self.thread_read.daemon = True
        self.thread_name = thread_name if thread_name else 'reader'
        self.thread_read.name = self.thread_name
        self.thread_read.start()

    def open_port(self):
        pass

    def stop(self):
        """Stop copying"""
        self.log.debug('stopping thread: {}'.format(self.thread_name))
        if self.alive:
            self.alive = False
            self.thread_read.join()

