import serial
import sys
import glob
import json


class SerialOpenPortException(serial.SerialException):
    pass


FC_SERIAL_CMB_PORT, FC_SERIAL_CMB_BAUDRATE, FC_SERIAL_CMB_PARITY, FC_SERIAL_CMB_STOPBITS, FC_SERIAL_CMB_DATABITS = (
    'port_cmb', 'baud_rate_cmb', 'parity_cmb', 'stop_bits_cmb', 'databits_cmb')


class FillControlSerial(object):
    def __init__(self, log):
        self.serial = None
        self.__PARITIES = ('none', 'even', 'odd')
        self.__BAUDRATES = [str(b) for b in (50, 75, 110, 134, 150, 200, 300, 600, 1200, 1800, 2400, 4800,
                            9600, 19200, 38400, 57600, 115200, 128000, 153600, 230400, 256000,
                            460800, 921600)]
        self.__DATABITS = [str(db) for db in (5, 6, 7, 8)]
        self.__STOPBITS = [str(sb) for sb in (1, 1.5, 2)]
        self.__settings_default = {FC_SERIAL_CMB_BAUDRATE: self.baud_rates[13],
                                   FC_SERIAL_CMB_DATABITS: self.data_bits[-1],
                                   FC_SERIAL_CMB_PARITY: self.parities[0], FC_SERIAL_CMB_PORT: 'COM1',
                                   FC_SERIAL_CMB_STOPBITS: self.stop_bits[0]}
        self.log = log

    @property
    def baud_rates(self):
        return self.__BAUDRATES

    @property
    def data_bits(self):
        return self.__DATABITS

    @property
    def parities(self):
        return self.__PARITIES

    @property
    def stop_bits(self):
        return self.__STOPBITS

    def load_serial_settings(self, filename):
        try:
            with open(filename, 'rt', encoding='utf-8') as file:
                settings = json.loads(file)
            if settings and settings.get('serial'):
                return settings.get('serial')
        except Exception:
            self.log.info('!INFO: Didn\'t load file settings for serial')
        return self.__settings_default

    def init_controls(self, filename, port_cmb, baud_rate_cmb, parity_cmb, stop_bits_cmb, databits_cmb):
        list_ports = self.get_serial_ports()
        port_cmb.addItems(list_ports)
        baud_rate_cmb.addItems(self.baud_rates)
        databits_cmb.addItems(self.data_bits)
        stop_bits_cmb.addItems(self.stop_bits)
        parity_cmb.addItems(self.parities)

        try:
            settings = self.load_serial_settings(filename)

            if settings[FC_SERIAL_CMB_PORT] in list_ports:
                port_cmb.setCurrentIndex(list_ports.index(settings[FC_SERIAL_CMB_PORT]))
            if settings[FC_SERIAL_CMB_STOPBITS] in self.stop_bits:
                stop_bits_cmb.setCurrentIndex(self.stop_bits.index(settings[FC_SERIAL_CMB_STOPBITS]))
            if settings[FC_SERIAL_CMB_DATABITS] in self.data_bits:
                databits_cmb.setCurrentIndex(self.data_bits.index(settings[FC_SERIAL_CMB_DATABITS]))
            if settings[FC_SERIAL_CMB_BAUDRATE] in self.baud_rates:
                baud_rate_cmb.setCurrentIndex(self.baud_rates.index(settings[FC_SERIAL_CMB_BAUDRATE]))
            if settings[FC_SERIAL_CMB_PARITY] in self.parities:
                parity_cmb.setCurrentIndex(self.parities.index(settings[FC_SERIAL_CMB_PARITY]))
        except Exception as err:
            self.log.error('!ERROR: Invalid parsing init control: {}'.format(err))
            # print('!ERROR: Invalid parsing init control: {}'.format(err))

    # def __init_serial(self, **serial_settings):
    #     self.serial = serial.Serial()
    #     if not serial_settings.get('port'):
    #         return None
    #     try:
    #         self.serial.port = serial_settings.get('port')  # , do_not_open=True)
    #         self.serial.timeout = 0  # required so that the reader thread can exit
    #         self.serial.baudrate = serial_settings.get('baud_rate')
    #         self.serial.parity = self.__get_parity(serial_settings.get('parity'))
    #         self.serial.stopbits = self.__get_stop_bits(serial_settings.get('stop_bits'))
    #         self.serial.bytesize = self.__get_databits(serial_settings.get('databits'))
    #     except Exception as err:
    #         exc_str = "!ERROR: Invalid class port settings: {}".format(serial_settings)
    #         raise SerialOpenPortException(exc_str) from err
    #     return True

    def __get_parity(self, parity_str):
        if parity_str.lower().strip() == self.__PARITIES[0]:
            parity = serial.PARITY_NONE
        elif parity_str.lower().strip() == self.__PARITIES[1]:
            parity = serial.PARITY_EVEN
        elif parity_str.lower().strip() == self.__PARITIES[2]:
            parity = serial.PARITY_ODD
        else:
            raise ValueError("Serial settings: invalid value parity: {}"
                             " [none, even, odd]".format(parity_str))
        return parity

    def __get_stop_bits(self, stop_bits_str):
        stop_bits = int(stop_bits_str)
        if stop_bits not in self.__STOPBITS:
            raise ValueError("Serial settings: invalid value stop bits:"
                             " {} [{}]".format(stop_bits_str, self.__STOPBITS))
        return stop_bits

    def __get_databits(self, data_bits_str):
        data_bits = int(data_bits_str)
        if data_bits not in self.__DATABITS:
            raise ValueError("Serial settings: invalid value databits:"
                             " {} [{}]".format(data_bits_str, self.__DATABITS))
        return data_bits

    def get_serial_ports(self):
        """ Lists serial port names

            :raises EnvironmentError:
                On unsupported or unknown platforms
            :returns:
                A list of the serial ports available on the system
        """
        if sys.platform.startswith('win'):
            ports = ['COM%s' % (i + 1) for i in range(256)]
        elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
            # this excludes your current terminal "/dev/tty"
            ports = glob.glob('/dev/tty[A-Za-z]*')
        elif sys.platform.startswith('darwin'):
            ports = glob.glob('/dev/tty.*')
        else:
            raise EnvironmentError('Unsupported platform')

        result = []
        for port in ports:
            try:
                s = serial.Serial(port)
                s.close()
                result.append(port)
            except (OSError, serial.SerialException):
                pass
        return result


if __name__ == '__main__':
    import logging
    print(FillControlSerial(logging.getLogger('serial')).get_serial_ports())
