#!/usr/bin/env python
# -*- coding=utf-8 -*-
import copy
import errno
import socket
from PyQt4 import QtCore

from imitator_device.protocol.handling_protocol import HandlingProtocol
from imitator_device.server_device_imitator import ThreadServerDeviceImitator
from imitator_device.interfaces.socket.ClientThread import ClientTcpThread
from tools_binary import byte2hex_str


class SocketBindPortException(socket.error):
    pass


class SocketDeviceException(Exception):
    def __init__(self, err):
        super(SocketDeviceException, self).__init__(err)


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


class ServerSocketDeviceimitator(ThreadServerDeviceImitator):
    """
    """
    sig_client_added = QtCore.pyqtSignal(str)
    sig_client_removed = QtCore.pyqtSignal(int)

    def __init__(self, settings_conf: HandlingProtocol, logger, control_gui=None, parent=None):
        super(ServerSocketDeviceimitator, self).__init__(logger, parent)
        self.buffer_size = 1024
        self.socket = None
        self.__control_gui = control_gui
        self.handler_response = settings_conf.handler_response
        self.socket_settings = settings_conf.socket_settings
        self.handler_emit_send = settings_conf.handler_emit_send
        self.__threads_pool = {}
        # self.__init_socket()

    def __init_socket(self):
        try:
            self.socket = socket.socket(socket.AF_INET, self.socket_settings.socket_type)
            # self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        except Exception as err:
            exc_str = "!Error: Invalid class port settings: {}".format(self.socket_settings)
            self.log.error(exc_str)
            raise SocketBindPortException(exc_str) from err

    def __str__(self):
        return 'ServerSocketDeviceimitator(status={}, settings={})'.format(self.running,
                                                                           self.socket_settings.__repr__())

    def get_address(self):
        return self.socket_settings.host, self.socket_settings.port

    def open_address(self, address_bind, is_blocking=False):
        self.__init_socket()
        self.socket_settings.host, self.socket_settings.port = address_bind
        try:
            self.socket.bind(address_bind)
            self.socket.setblocking(int(is_blocking))
            # self.socket.settimeout(0.5)
        except socket.error as err:
            exc_str = "!ERROR:  Bind socket failed on port {}. Error message: {}".format(self.socket_settings.port,
                                                                                         err.args)
            self.log.error(exc_str)
            return False
            # raise SocketBindPortException(exc_str) from err
        return True

    def open(self):
        return self.open_address((self.socket_settings.host, self.socket_settings.port))

    def listen_address(self, address_bind, amount_tcp_clients=1, thread_name='socket-reader'):
        if self.open_address(address_bind) and self.socket:
            name = self.socket.getsockname()[0] + ':' + str(self.socket.getsockname()[1])
            super(ServerSocketDeviceimitator, self).listen(thread_name=name)
            if self.socket_settings.socket_type == socket.SOCK_STREAM:
                self.socket.listen(amount_tcp_clients)
                # super().listen(qthread_name='tcp-reader')
            elif self.socket_settings.socket_type == socket.SOCK_DGRAM:
                pass
                # super().listen(qthread_name='udp-reader')
            else:
                return False
            return True
        return False

    def listen(self, amount_tcp_clients=1, thread_name='socket-reader'):
        return self.listen_address((self.socket_settings.host, self.socket_settings.port),
                                   amount_tcp_clients=amount_tcp_clients, thread_name=thread_name)

    def stop(self):
        for client in self.__threads_pool:
            client.stop()
        super(ServerSocketDeviceimitator, self).stop()
        # for client in self.__list_threads:
        #     client.terminate()

    @deco_reader
    def reader(self):
        pass

    def _reader_udp(self):
        """loop forever and handling packets protocol"""
        try:
            while self.running:
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
                        self.__process_packet_udp(addr, data_recv)
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
            self.socket.shutdown(socket.SHUT_RD)
            self.socket.close()

    def __process_packet_udp(self, addr, data_recv):
        self.log.info("======================================")
        self.log.info("-> recv: {} from {}".format(byte2hex_str(data_recv), addr))
        list_packets = self.handler_response(self.log, data_recv, self.__control_gui)
        if list_packets:
            for packet in list_packets:
                if packet:
                    self.log.info("<- send: {} to {}".format(byte2hex_str(packet), addr),
                                  extra=self.log_var)
                    self.socket.sendto(packet, addr)

    def __del_client(self, result):
        client_thread = self.sender()
        del self.__threads_pool[client_thread]
        self.sig_client_added.emit(client_thread.get_str_client())

    def _reader_tcp(self):
        """loop forever and handling packets protocol"""
        # client = None
        try:
            while self.running:
                try:
                    try:
                        client, addr = self.socket.accept()
                    except socket.error:  # данных нет
                        pass  # тут ставим код выхода
                    else:  # данные есть
                        self.log.error('Connecting client from: {}'.format(addr))
                        thread_logger = copy.copy(self.log)
                        thread_name = '{}:{}<=>{}:{}'.format(*self.get_address(), *addr)
                        client_thread = ClientTcpThread(thread_logger, client=client, address=addr,
                                                 handlers=(
                                                     self.handler_emit_send, self.handler_response, self.__control_gui),
                                                 thread_name=thread_name,
                                                 buffer_size=self.buffer_size,
                                                 )
                        client_thread.sig_job_finished.connect(self.__del_client)
                        client_thread.start()
                        self.__threads_pool[client_thread] = addr
                        self.sig_client_added.emit(client_thread.get_str_client())
                        # self.log.qthread_name = 'client=' + str(addr)
                        # client.setblocking(0)  # снимаем блокировку и тут тоже
                        # for packet in self.handler_emit_send(self.log, self.__control_gui, is_connect=True):
                        #     if packet:
                        #         client.send(packet)
                        #         self.log.warning("<- send: {}".format(byte2hex_str(packet)))
                        #
                        # # если в блоке except вы выходите,
                        # # ставить else и отступ не нужно
                        # while self.running:
                        #     try:
                        #         for packet in self.handler_emit_send(self.log, self.__control_gui, is_timeout=True):
                        #             if packet:
                        #                 client.send(packet)
                        #                 self.log.warning("<- send <timeout>: {} ".format(byte2hex_str(packet)))
                        #
                        #         data_recv = client.recv(self.buffer_size)
                        #     except socket.error as err:  # данных нет
                        #         if err.args[0] == errno.EWOULDBLOCK or err.args[0] == errno.EAGAIN:
                        #             # self.log.debug('EWOULDBLOCK')
                        #             # time.sleep(0.1)           # short delay, no tight loops
                        #             continue
                        #         elif err.args[0] == errno.WSAECONNABORTED:
                        #             self.log.error('>> Client closed connection from {}'.format(addr))
                        #             break
                        #         elif err.args[0] == errno.WSAECONNRESET:
                        #             self.log.error('>> Client break down connection from {}'.format(addr))
                        #             break
                        #         else:
                        #             client.close()
                        #             self.log.error('Connection close')
                        #             raise Exception("error") from err
                        #     else:  # данные есть
                        #         if not data_recv:
                        #             break
                        #         else:
                        #             self.__process_packet_tcp(client, data_recv)
                        # client.close()
                except socket.error as err:
                    if err.args[0] == errno.WSAECONNABORTED:
                        self.log.error('!Error: Connection abort from {}: {}'.format(addr, err.args[1]))
                        continue
                    elif err.args[0] == errno.WSAECONNRESET:
                        self.log.error('!Error: Connection reset from {}: {}'.format(addr, err.args[1]))
                        continue
                    else:
                        raise socket.error(err)
        # ----------------------------------------------------------------------------
        except socket.error as err:
            exc_str = "!ERROR: Something else happened on read/write to socket: {}".format(err.args)
            self.log.error(exc_str)
            raise SocketDeviceException(exc_str) from err
        except ValueError as err:
            exc_str = "!ERROR: Occurrence into handlers for process packets: {}".format(err.args)
            self.log.error(exc_str)
            raise SocketDeviceException(exc_str) from err
        except Exception as err:
            exc_str = "!ERROR: Occurrence unknown mistake  at time process packets: {}".format(err.args)
            self.log.error(exc_str)
            raise SocketDeviceException(exc_str) from err
        finally:
            try:
                self.socket.shutdown(socket.SHUT_RD)
            except:
                pass
            self.socket.close()
            pass


def socket_server_start(settings_conf, logger, control_gui=None, parent=None):
    is_socket_server_start = False
    socket_server = None
    try:
        socket_server = ServerSocketDeviceimitator(settings_conf, logger, control_gui)
        logger.info("Serving socket port: {}".format(settings_conf.socket_settings))
        is_socket_server_start = socket_server.listen(amount_tcp_clients=5)
    except SocketBindPortException as err:
        print(err)
    except Exception as err:
        raise SocketDeviceException(err) from err
    finally:
        if socket_server and not is_socket_server_start:
            socket_server.stop()
            socket_server = None
            logger.info('Disconnected socket interface: {}'.format(socket_server))
    return socket_server
