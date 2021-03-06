#!/usr/bin/env python
# -*- coding=utf-8 -*-

from PyQt5 import QtCore


class WorkerThread(QtCore.QThread):
    sig_job_finished = QtCore.pyqtSignal(bool)
    sig_req_values_form = QtCore.pyqtSignal(name='req_values_form')
    sig_status_thread = QtCore.pyqtSignal(bool, name='status_thread')

    def __init__(self, logger, thread_name='WorkerThread', parent=None):
        super(WorkerThread, self).__init__(parent)
        self.running = False
        self.log = logger
        self.thread_name = thread_name

    def __del__(self):
        self.wait()

    def run(self):
        self.running = True
        self.log.qthread_name = self.thread_name
        self.log.system('Thread {} start'.format(self.thread_name))
        self.sig_status_thread.emit(True)
        success = self._do_work()
        self.sig_job_finished.emit(bool(success))
        self.log.system('{} thread terminated'.format(self.thread_name))

    def stop(self):
        self.running = False
        self.log.system('Thread {} stop (WorkerThread)'.format(self.thread_name))

    @property
    def status(self):
        return self.running

    def _do_work(self):
        return True

    def clean_up(self):
        pass


class ThreadServerDeviceImitator(WorkerThread):
    def __init__(self, logger, parent=None):
        super(ThreadServerDeviceImitator, self).__init__(logger, 'ThreadServerDeviceImitator', parent)
        self.log = logger
        self.thread_read = None
        self.running = False
        self.dict_values_form = {}

    @QtCore.pyqtSlot(dict)
    def slot_values_form_changed(self, dict_values_form):
        self.dict_values_form = dict_values_form
        self.handler_response_form_values()

    def handler_response_form_values(self):
        pass

    def _do_work(self):
        """loop forever and handling packets protocol"""
        try:
            self.reader()
        finally:
            self.running = False

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
        """Stop thread"""
        self.log.debug('stopping thread: {}'.format(self.thread_name))
        super(ThreadServerDeviceImitator, self).stop()

