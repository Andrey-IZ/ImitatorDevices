#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import serial
import threading
import sys
import handlers_ukcu as handlers
from tools_binary import byte2hex_str
from imitator_serial_device import FoldingSettings


class SerialServer(object):
    def __init__(self, serial_instance, settings):
        self.serial = serial_instance
        self._write_lock = threading.Lock()
        self.log = logging.getLogger('SerialServer')
        self.data_req = handlers.handler_request_setup_ukcu()
        self.thread_read = None
        self.alive = False
        self.__settings = settings

    def reader(self):
        """loop forever and copy serial->socket"""
        self.log.debug('reader thread started')
        i = 0
        while self.alive:
            data_recv = self.serial.read(self.serial.in_waiting)
            if data_recv:
                self.log.debug("======================================")
                self.log.debug("-> recv: {}".format((byte2hex_str(data_recv))))
                # escape outgoing data when needed (Telnet IAC (0xff) character)
                # self.write(serial.to_bytes(self.rfc2217.escape(data)))
                list_packets = self.__settings.handler_response(data_recv)
                if list_packets:
                    for packet in list_packets:
                        if packet:
                            self.log.debug("<- send: {}".format(byte2hex_str(packet)))
                            ser.write(packet)

                # if i < 2 and data_recv == self.data_req[i][0]:
                #     wr_data = handlers.handler_ukcu_response(data_recv, self.data_req[i])
                #     self.log.debug("<- send: {}".format((wr_data)))
                #     ser.write(wr_data)
                #     i += 1
        self.alive = False
        self.log.debug('reader thread terminated')

    def listen(self):
        """connect the serial port to the TCP port by copying everything
           from one side to the other"""
        self.alive = True
        self.thread_read = threading.Thread(target=self.reader)
        self.thread_read.daemon = True
        self.thread_read.name = 'serial-reader'
        self.thread_read.start()

    def stop(self):
        """Stop copying"""
        self.log.debug('stopping')
        if self.alive:
            self.alive = False
            self.thread_read.join()


if __name__ == '__main__':
    logging.basicConfig(format=u'%(asctime)-15s [%(threadName)s] %(message)s',
                        level=logging.DEBUG)
    file_conf = 'protocol_serial_device.conf'
    settings_conf = FoldingSettings()
    logging.info("Parsing configuration file: {}".format(file_conf))
    settings_conf.parse(file_conf)
    logging.info("Imitator serial devices start")

    # connect to serial port
    ser = serial.serial_for_url('COM2', do_not_open=True)
    ser.timeout = 3     # required so that the reader thread can exit
    # reset control line as no _remote_ "terminal" has been connected yet
    ser.dtr = False
    ser.rts = False

    try:
        ser.open()
    except serial.SerialException as e:
        logging.error("Could not open serial port {}: {}".format(ser.name, e))
        sys.exit(1)

    cmd = ''
    serial_settings = ser.getSettingsDict()

    while True:
        print(u">>> Imitator serial device is started.  Enter 'exit' for quit. Enter 'start' to start server")
        try:
            logging.info("Serving serial port: {}".format(ser.name))
            ser.rts = True
            ser.dtr = True
            r = SerialServer(ser, settings_conf)
            try:
                r.listen()
                while True:
                    cmd = input()
                    if cmd == 'stop' or cmd == 'exit':
                        break
            finally:
                logging.info('Disconnected')
                r.stop()
                ser.dtr = False
                ser.rts = False
                # Restore port settings (may have been changed by RFC 2217
                # capable client)
                ser.apply_settings(serial_settings)
                print(u">>> Imitator serial device was stop")
        except KeyboardInterrupt:
            sys.stdout.write('\n')
            break

        if cmd == 'exit':
            break

        while True:
            cmd = input()
            if cmd == 'start':
                break

    logging.info('--- exit ---')