#!/usr/bin/env python
# -*- coding=utf-8 -*-

import select
import time
import errno
import socket
from ImitatorDevice.server_device_imitator import ServerDeviceImitator
from tools_binary import byte2hex_str
import socketserver
from ImitatorDevice.socket.socket_settings import SocketSettings


class SocketBindPortException(socket.error):
    pass


class SocketDeviceException(Exception):
    pass


class ThreadedTCPRequestHandler(socketserver.BaseRequestHandler):
    def handle(self):
        data = self.request.recv(1024)
        cur_thread = threading.current_thread()
        response = "{}: {}".format(cur_thread.name, data)
        self.request.sendall(response)


class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    pass


def deco_reader(fn):
    """

    :param func:
    :rtype: function
    """

    def wrapper(self, *args, **kwargs):
        if self.socket_settings.socket_type == socket.SOCK_STREAM:
            return self._reader_tcp()
        if self.socket_settings.socket_type == socket.SOCK_DGRAM:
            return self._reader_udp()

    return wrapper


class ServerSocketDeviceimitator(ServerDeviceImitator):
    """
    """

    def __init__(self, settings_conf, buffer_size=1024):
        super().__init__('Socket Server')
        self.buffer_size = buffer_size
        self.socket = None
        self.func_process_events = None
        self.handler_response = settings_conf.handler_response
        self.socket_settings = settings_conf.socket_settings
        self.__init_socket()

    def __init_socket(self):
        try:
            self.socket = socket.socket(socket.AF_INET, self.socket_settings.socket_type)
        except Exception as err:
            exc_str = "!Error: Invalid class port settings: {}".format(self.socket_settings)
            self.log.error(exc_str)
            raise SocketBindPortException(exc_str) from err

    def open_port(self):
        try:
            self.socket.bind((self.socket_settings.host, self.socket_settings.port))
            self.socket.setblocking(0)

            if self.socket_settings.socket_type == socket.SOCK_STREAM:
                pass
                # self.socket.connect((self.socket_settings.host, self.socket_settings.port))
                # self.socket.settimeout(0)
            if self.socket_settings.socket_type == socket.SOCK_DGRAM:
                pass
                # self.socket.setblocking(0)
                # self.socket.bind((self.socket_settings.host, self.socket_settings.port))
        except socket.error as err:
            exc_str = "!ERROR:  Bind socket failed on port {}. Error message: {}".format(self.socket_settings.port,
                                                                                         err.args)
            self.log.error(exc_str)
            raise SocketBindPortException(exc_str) from err
        return True

    def listen(self, amount_tcp_clients=1, thread_name='socket-reader'):
        if self.socket:
            if self.socket_settings.socket_type == socket.SOCK_STREAM:
                self.socket.listen(amount_tcp_clients)
                super().listen(thread_name='tcp-reader')
            elif self.socket_settings.socket_type == socket.SOCK_DGRAM:
                super().listen(thread_name='udp-reader')
            else:
                return False
            return True
        return False

    @deco_reader
    def reader(self):
        pass

    def _reader_udp(self):
        """loop forever and handling packets protocol"""
        try:
            while self.alive:
                try:
                    # end = time.time()
                    # elapsed = end - self.start_time
                    # if time_waiting:
                    #     if elapsed > time_waiting:
                    #         self.log.warning('REQUEST TIMED OUT')
                    #         self.notify_timeout_func(self.last_sending_button)
                    #         break
                    # else:
                    #     break
                    data_recv, addr = self.socket.recvfrom(self.buffer_size)
                except socket.timeout as e:
                    err = e.args[0]
                    # this next if/else is a bit redundant, but illustrates how the
                    # timeout exception is setup
                    if err == 'timed out':
                        # sleep(1)
                        self.log.warning('receive timed out, retry later')
                        continue
                    else:
                        print(e)
                except socket.error as e:
                    # Something else happened, handle error, exit, etc.
                    pass
                else:
                    if not data_recv:
                        text = 'server receive empty data !!!'
                        print(text)
                        self.log.debug(text + '\n')
                    else:  # ********** handling packets ******************
                        self.log.warning("======================================")
                        self.log.warning("-> recv: {} from {}".format(byte2hex_str(data_recv), addr))

                        list_packets = self.handler_response(data_recv)
                        if list_packets:
                            for packet in list_packets:
                                if packet:
                                    self.log.warning("<- send: {} to {}".format(byte2hex_str(packet), addr))
                                    self.socket.sendto(packet, addr)
                if self.func_process_events:
                    self.func_process_events()
        except socket.error as err:
            exc_str = "!ERROR: Something else happened on write to socket"
            self.log.error(exc_str)
            raise SocketDeviceException(exc_str) from err
        except ValueError as err:
            exc_str = "!ERROR: Occurrence into handlers for process packets"
            self.log.error(exc_str)
            raise SocketDeviceException(exc_str) from err
        except Exception as err:
            exc_str = "!ERROR: Occurrence unknown mistake  at time process packets"
            self.log.error(exc_str)
            raise SocketDeviceException(exc_str) from err
        finally:
            self.socket.close()

    def _reader_tcp(self):
        """loop forever and handling packets protocol"""
        try:
            while self.alive:
                try:
                    client, addr = self.socket.accept()
                except socket.error:  # данных нет
                    pass  # тут ставим код выхода
                else:  # данные есть
                    self.log.warning('Connecting client from: {}'.format(addr))
                    client.setblocking(0)  # снимаем блокировку и тут тоже
                    # если в блоке except вы выходите,
                    # ставить else и отступ не нужно
                    while self.alive:
                        try:
                            data_recv = client.recv(self.buffer_size)
                        except socket.error as err:  # данных нет
                            if err.args[0] == errno.EWOULDBLOCK or err.args[0] == errno.EAGAIN:
                                # or e.args[0] == errno.WSAENOTCONN:
                                # print('EWOULDBLOCK')
                                # time.sleep(0.1)           # short delay, no tight loops
                                continue
                            else:
                                client.close()
                                raise Exception("error") from err
                        else:  # данные есть
                            if data_recv:
                                self.log.warning("======================================")
                                self.log.warning("-> recv: {}".format((byte2hex_str(data_recv))))
                                list_packets = self.handler_response(data_recv)
                                if list_packets:
                                    for packet in list_packets:
                                        if packet:
                                            self.log.warning("<- send: {}".format(byte2hex_str(packet)))
                                            client.send(packet)
                                        # -----------------------------------------------
        except socket.error as err:
            exc_str = "!ERROR: Something else happened on read/write to socket"
            self.log.error(exc_str)
            raise SocketDeviceException(exc_str) from err
        except ValueError as err:
            exc_str = "!ERROR: Occurrence into handlers for process packets"
            self.log.error(exc_str)
            raise SocketDeviceException(exc_str) from err
        except Exception as err:
            exc_str = "!ERROR: Occurrence unknown mistake  at time process packets"
            self.log.error(exc_str)
            raise SocketDeviceException(exc_str) from err
        finally:
            self.socket.close()