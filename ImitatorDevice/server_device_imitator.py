import threading
import logging
from tools_binary import byte2hex_str


class ServerDeviceImitator(object):
    def __init__(self, settings, func_writer, func_reader, arg_reader_func=None):
        self.__func_reader = func_reader
        self.__func_write = func_writer
        self.__reader_arg = arg_reader_func
        self._write_lock = threading.Lock()
        self.log = logging.getLogger('SerialServer')
        self.thread_read = None
        self.alive = False
        self.__settings = settings

    def __un_func_reader(self):
        if self.__reader_arg is None:
            return self.__func_reader()
        elif isinstance(self.__reader_arg, tuple) and len(self.__reader_arg) == 2:
            if hasattr(self.__reader_arg[0], '__call__'):
                if self.__reader_arg[1] == 'call':
                    return self.__func_reader(self.__reader_arg[0]())
                else:
                    return self.__func_reader(self.__reader_arg[0])
        elif hasattr(self.__reader_arg, '__call__'):
                return self.__func_reader(getattr(self.__reader_arg[0], self.__reader_arg[1]))
        return None

    def reader(self):
        """loop forever and handling packets protocol"""
        self.log.debug('reader thread started')
        i = 0
        while self.alive:
            data_recv = self.__un_func_reader()#self.serial.read(self.serial.in_waiting)
            if data_recv:
                self.log.warning("======================================")
                self.log.warning("-> recv: {}".format((byte2hex_str(data_recv))))

                list_packets = self.__settings.handler_response(data_recv)
                if list_packets:
                    for packet in list_packets:
                        if packet:
                            self.log.warning("<- send: {}".format(byte2hex_str(packet)))
                            self.__func_write(packet)
                            # self.serial.write(packet)
        self.alive = False
        self.log.debug('reader thread terminated')

    def listen(self):
        self.alive = True
        self.thread_read = threading.Thread(target=self.reader)
        self.thread_read.daemon = True
        self.thread_read.name = 'reader'
        self.thread_read.start()

    def stop(self):
        """Stop copying"""
        self.log.debug('stopping')
        if self.alive:
            self.alive = False
            self.thread_read.join()

