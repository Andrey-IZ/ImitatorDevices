import time

from PyQt5 import QtCore

from gui.gui_tools.fill_control.fill_control_serial import FillControlSerial
from gui.gui_tools.fill_control.fill_control_socket import FillControlSocket


class GuiControlsReload(object):
    def __init__(self):
        self.__gui_protocol = None
        self.__fill_control_param = {'socket': (), 'serial': ()}
        self.__file_config = None
        self.__params = None
        self.__settings_conf = None
        self.__is_init_server = None

    def check_content(self) -> list:
        list_invalid_attr = []
        for attr, value in self.__dict__.items():
            if value is None:
                list_invalid_attr.append((attr, value))
        return list_invalid_attr

    @property
    def params_console(self):
        return self.__params

    @params_console.setter
    def params_console(self, value):
        self.__params = value

    @property
    def file_config(self):
        return self.__file_config

    @file_config.setter
    def file_config(self, value):
        self.__file_config = value

    @property
    def fill_control_param(self):
        return self.__fill_control_param

    @fill_control_param.setter
    def fill_control_param(self, value):
        self.__fill_control_param = value

    @property
    def settings_conf(self):
        return self.__settings_conf

    @settings_conf.setter
    def settings_conf(self, value):
        self.__settings_conf = value

    @property
    def is_init_server(self):
        return self.__is_init_server

    @is_init_server.setter
    def is_init_server(self, value):
        self.__is_init_server = value

    @property
    def gui_protocol(self):
        return self.__gui_protocol

    @gui_protocol.setter
    def gui_protocol(self, value):
        if value:
            self.__gui_protocol = value


class GuiReload(QtCore.QThread):
    sig_job_finished = QtCore.pyqtSignal(bool)
    sig_start_new_job = QtCore.pyqtSignal()
    sig_status_thread = QtCore.pyqtSignal(object, name='status_thread')

    def __init__(self, logger, controls_reload: GuiControlsReload, thread_name='reload_gui', parent=None):
        super(GuiReload, self).__init__(parent)
        self.__running = False
        self.__log = logger
        self.__thread_name = thread_name
        self.controls_reload = controls_reload

    def run(self):
        self.__running = True
        self.__log.qthread_name = self.__thread_name
        self.__log.system('************* INIT ******************************')
        self.sig_status_thread.emit(True)
        success = self._do_work()
        self.sig_status_thread.emit(success)
        self.__log.system('Reload is finished'.format(self.__log.qthread_name))
        self.sig_job_finished.emit(bool(success))
        self.__log.system('************************************************')
        self.sig_start_new_job.emit()

    def stop(self):
        self.__running = False
        self.__log.system('Reload gui is stopped'.format(self.thread_name))

    @property
    def status(self):
        return self.__running

    def _do_work(self):
        if not self.controls_reload.check_content():
            result = True
            try:
                self.__parse_config()
                self.__init_gui_form()
            except:
                result = False
            finally:
                return result
        return None

    def __parse_config(self):
        self.__log.info("Parsing configuration file: {}".format(self.controls_reload.file_config))
        try:
            stat = self.controls_reload.settings_conf.parse(self.controls_reload.file_config, self.controls_reload.gui_protocol)
            if self.controls_reload.params_console.is_show_stat:
                self.__log.info("Results parsing file {}:".format(self.controls_reload.file_config) + stat)
        except Exception as err:
            self.__log.error('>>> {}'.format(err))
            raise Exception(err) from err

    def __init_gui_form(self):
        if self.controls_reload.is_init_server:
            control_socket = FillControlSocket(self.__log, self.controls_reload.settings_conf.socket_settings)
            control_socket.init_controls(*self.controls_reload.fill_control_param['socket'])

            control_serial = FillControlSerial(self.__log, self.controls_reload.settings_conf.serialport_settings)
            control_serial.init_controls(*self.controls_reload.fill_control_param['serial'])
