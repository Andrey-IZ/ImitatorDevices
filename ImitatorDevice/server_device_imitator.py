#!/usr/bin/env python
# -*- coding=utf-8 -*-

from PyQt4 import QtCore
import logging


class WorkerThread(QtCore.QThread):
    sig_job_finished = QtCore.pyqtSignal(bool)
    sig_add_log = QtCore.pyqtSignal(str, name='add_log')
    sig_req_values_form = QtCore.pyqtSignal(name='req_values_form')
    sig_status_thread = QtCore.pyqtSignal(bool, name='status_thread')

    def __init__(self, thread_name='WorkerThread'):
        super(WorkerThread, self).__init__()
        self.running = False
        self.thread_name = thread_name

    def run(self):
        self.running = True
        self.sig_add_log.emit('Thread {} start'.format(self.thread_name))
        self.sig_status_thread.emit(True)
        success = self._do_work()
        self.sig_job_finished.emit(bool(success))

    def stop(self):
        self.running = False
        self.sig_add_log.emit('Thread stop')

    @property
    def status(self):
        return self.running

    def _do_work(self):
        return True

    def clean_up(self):
        pass


class ThreadServerDeviceImitator(WorkerThread):
    def __init__(self, logger):
        super(ThreadServerDeviceImitator, self).__init__('thread')
        self.log = logger
        self.thread_read = None
        self.running = False
        self.dict_values_form = {}

    @QtCore.pyqtSlot(dict)
    def slot_values_form_changed(self, dict_values_form):
        self.dict_values_form = dict_values_form

    def _do_work(self):
        """loop forever and handling packets protocol"""
        self.log.warning('{} thread started'.format(self.thread_name))
        try:
            self.reader()
        finally:
            self.running = False
            self.log.warning('{} thread terminated'.format(self.thread_name))

    def reader(self):
        pass

    def get_address(self):
        pass

    def listen(self, thread_name):
        self.running = True
        self.thread_name = thread_name
        # self.thread_read = threading.Thread(target=self.run)
        super(ThreadServerDeviceImitator, self).start()

    def open(self):
        pass

    def stop(self):
        """Stop copying"""
        self.log.debug('stopping thread: {}'.format(self.thread_name))
        super(ThreadServerDeviceImitator, self).stop()

