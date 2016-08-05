#!/usr/bin/env python
# -*- coding=utf-8 -*-

import errno
import socket
from PyQt4 import QtCore
from tools_binary import byte2hex_str


class ClientTcpThread(QtCore.QThread):
    sig_job_finished = QtCore.pyqtSignal(bool)

    def __init__(self, logger, client, address, handlers, thread_name='WorkerThread', buffer_size=1024, parent=None):
        super(ClientTcpThread, self).__init__(parent)
        self.__log = logger
        self.__running = False
        self.__thread_name = thread_name
        self.__client = client
        self.__address = address
        self.__handler_emit_send, self.__handler_response, self.__control_gui = handlers
        self.__buffer_size = buffer_size

    def run(self):
        self.__running = True
        self.__log.qthread_name = self.__thread_name
        self.__log.system('Thread {} start'.format(self.__thread_name))
        success = self._do_work()
        self.sig_job_finished.emit(bool(success))
        self.__log.system('{} thread terminated'.format(self.__thread_name))

    def __del__(self):
        self.wait()

    def stop(self):
        self.__running = False
        self.__log.system('Thread {} stop (WorkerThread)'.format(self.__thread_name))

    @property
    def client(self):
        return self.__client

    @property
    def address(self):
        return self.__address

    def get_str_client(self):
        return '{}:{}'.format(*self.address)

    @property
    def status(self):
        return self.__running

    def _do_work(self):
        try:
            # self.__log.qthread_name = 'client=' + str(self.__address)
            self.__client.setblocking(0)  # снимаем блокировку и тут тоже
            for packet in self.__handler_emit_send(self.__log, self.__control_gui, is_connect=True):
                if packet:
                    self.__client.send(packet)
                    self.__log.warning("<- send: {}".format(byte2hex_str(packet)))

            # если в блоке except вы выходите,
            # ставить else и отступ не нужно

            while self.__running:
                try:
                    for packet in self.__handler_emit_send(self.__log, self.__control_gui, is_timeout=True):
                        if packet:
                            self.__client.send(packet)
                            self.__log.warning("<- send <timeout>: {} ".format(byte2hex_str(packet)))

                    data_recv = self.__client.recv(self.__buffer_size)
                except socket.error as err:  # данных нет
                    if err.args[0] == errno.EWOULDBLOCK or err.args[0] == errno.EAGAIN:
                        # self.log.debug('EWOULDBLOCK')
                        # time.sleep(0.1)           # short delay, no tight loops
                        continue
                    elif err.args[0] == errno.WSAECONNABORTED:
                        self.__log.error('>> Client closed connection from {}'.format(self.__address))
                        break
                    elif err.args[0] == errno.WSAECONNRESET:
                        self.__log.error('>> Client break down connection from {}'.format(self.__address))
                        break
                    else:
                        self.__client.close()
                        self.__log.error('Connection close')
                        raise Exception("error") from err
                else:  # данные есть
                    if not data_recv:
                        break
                    else:
                        self.__process_packet_tcp(data_recv)
        finally:
            self.__client.close()

    def __process_packet_tcp(self, data_recv):
        self.__log.warning("======================================")
        self.__log.warning("-> recv: {}".format((byte2hex_str(data_recv))))
        list_packets = self.__handler_response(self.__log, data_recv, self.__control_gui)
        if list_packets:
            for packet in list_packets:
                if packet:
                    self.__log.warning("<- send: {}".format(byte2hex_str(packet)))
                    self.__client.send(packet)
