import sys
from PyQt4 import QtGui, uic
from PyQt4.Qt import *
from gui.main_window_ui import Ui_MainWindow
from gui.gui_tools.fill_control.fill_control_serial import FillControlSerial
from gui.gui_tools.fill_control.fill_control_socket import FillControlSocket
from ImitatorDevice.socket.ServerSocketDeviceImitator import socket_server_start, ServerSocketDeviceimitator
from ImitatorDevice.serial.ServerSerialDeviceImitator import serial_server_start, ServerSerialDeviceimitator
from gui.qt_logging import XStream
import copy
import re


class MainForm(QtGui.QMainWindow):
    sig_reply_req_values_form = pyqtSignal(dict)

    def __init__(self, log, params, settings_conf, file_conf, parent=None):
        # Запускаем родительский конструктор
        super(MainForm, self).__init__(parent)
        # *********************************
        # Подцепляем форму
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        # *********************************
        # Загружаем форму "на лету"
        # self.ui = uic.loadUi("main_window.ui", self)
        # **********************************

        self.log = log
        self.file_conf = file_conf
        self.server_serial = None
        self.server_socket = None
        self.settings_conf = settings_conf
        self.params = params
        self.pattern_log = re.compile(
            r'(?P<date>\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d{3}) &lt;(?P<msg>[A-Z])&gt;'
            r' \[(?P<log_name>\w+)~(?P<thread_name>.*?)\]\s.*?', re.I)
        self.repl_str = r'<font color=gray>\g<date></font> &lt;<font color=red>\g<msg></font>&gt;' \
                        r' [<U>\g<log_name></U>~<font color="blue">\g<thread_name></font>] '

        # XStream.stderr().messageWritten.connect(self.add_log_err)
        XStream.stdout().messageWritten.connect(self.add_log)

        self.__parse_config()
        self.__init_gui_form()
        self.__init_servers(settings_conf)
        self.__init_connect()


        # self.__setup_model()
        # self.__init_udp_protocol()

    def __init_servers(self, settings_conf):
        if settings_conf.socket_settings.host:
            socket_logger = copy.copy(self.log)
            socket_logger.name = 'Socket'
            self.server_socket = socket_server_start(settings_conf, socket_logger)
            btn_start, btn_stop, grpb = self.ui.pushButtonStartNet, self.ui.pushButtonStopNet, self.ui.groupBox_Net
            if self.server_socket:
                self.__notify_launch_server('server start: "{}"'.format(self.server_socket, str(
                    self.server_socket.get_address())), btn_start, btn_stop, grpb, True)
        else:
            self.ui.dockWidget_Net.setVisible(False)
        if settings_conf.serialport_settings.port:
            btn_start, btn_stop, grpb = self.ui.pushButtonStart_Serial, self.ui.pushButtonStop_Serial, self.ui.groupBox_Serial
            serial_logger = copy.copy(self.log)
            serial_logger.name = 'Serial'
            self.server_serial = serial_server_start(settings_conf, serial_logger)
            if self.server_serial:
                self.__notify_launch_server('server start: "{}"'.format(self.server_serial, str(
                    self.server_serial.get_address())), btn_start, btn_stop, grpb, True)
        else:
            self.ui.dockWidget_Serial.setVisible(False)

    def __parse_config(self):
        self.log.info("Parsing configuration file: {}".format(self.file_conf))
        try:
            stat = self.settings_conf.parse(self.file_conf)
            if self.params.is_show_stat:
                self.log.info("Results parsing file {}:".format(self.file_conf) + stat)
        except Exception as err:
            self.log.error('>>> {}'.format(err))
            raise Exception(err) from err

    def __init_gui_form(self):
        control_socket = FillControlSocket(self.log, self.settings_conf.socket_settings)
        control_socket.init_controls(self.ui.spinBox_Port_Bind, self.ui.lineEditIpAddressBind)

        control_serial = FillControlSerial(self.log, self.settings_conf.serialport_settings)
        control_serial.init_controls(self.ui.comboBox_ListPorts, self.ui.comboBox_BaudRate,
                                     self.ui.comboBox_DataBits, self.ui.comboBox_StopBits, self.ui.comboBox_Parity)

    def __init_connect(self):
        self.ui.pushButtonStartNet.clicked.connect(self.start_net_server)
        self.ui.pushButtonStart_Serial.clicked.connect(self.start_serial_server)

        if self.server_socket:
            self.server_socket.sig_job_finished.connect(self.suddenly_stop_server)
            self.ui.pushButtonStopNet.clicked.connect(lambda: self.stop_server(self.server_socket))
        if self.server_serial:
            self.server_serial.sig_job_finished.connect(self.suddenly_stop_server)
            self.ui.pushButtonStop_Serial.clicked.connect(lambda: self.stop_server(self.server_serial))

        self.__init_connect_server(self.server_socket)
        self.__init_connect_server(self.server_serial)

    def __init_connect_server(self, server):
        if server:
            self.ui.spinBox_BSB.valueChanged.connect(server.slot_values_form_changed)

    def start_net_server(self):
        if not self.server_socket.running:
            self.log.info('Start qt server: {}'.format(self.server_socket))
            # server.sig_req_values_form.connect(self.parse_values_of_form)
            # self.sig_reply_req_values_form.connect(self.server_socket.slot_get_data_form)
            address_bind = str(self.ui.lineEditIpAddressBind.text()), int(self.ui.spinBox_Port_Bind.value())
            btn_start, btn_stop, grpb = self.ui.pushButtonStartNet, self.ui.pushButtonStopNet, self.ui.groupBox_Net
            self.__notify_launch_server('server start listen on address:' + str(address_bind), btn_start, btn_stop,
                                        grpb, True)
            if not self.server_socket.listen_address(address_bind):
                self.__notify_launch_server('error running server on address: ' + str(address_bind), btn_start,
                                            btn_stop, grpb, False)

    def start_serial_server(self):
        if not self.server_serial.running:
            self.log.info('Start qt server: {}'.format(self.server_serial))
            serialport_settings = self.settings_conf.serialport_settings
            btn_start, btn_stop, grpb = self.ui.pushButtonStart_Serial, self.ui.pushButtonStop_Serial, self.ui.groupBox_Serial
            self.__notify_launch_server('server start listen on address: {}'.format(serialport_settings), btn_start,
                                        btn_stop, grpb, True)
            if not self.server_serial.listen_port(serialport_settings):
                self.__notify_launch_server('error running server on address: {}'.format(serialport_settings),
                                            btn_start, btn_stop, grpb, False)

    def suddenly_stop_server(self, result):
        server = self.sender()
        if isinstance(server, ServerSerialDeviceimitator):
            btn_start, btn_stop, grpb = self.ui.pushButtonStart_Serial, self.ui.pushButtonStop_Serial, self.ui.groupBox_Serial
        elif isinstance(server, ServerSocketDeviceimitator):
            btn_start, btn_stop, grpb = self.ui.pushButtonStartNet, self.ui.pushButtonStopNet, self.ui.groupBox_Net
        else:
            btn_start, btn_stop, grpb = None, None, None

        if not result and server.status:
            self.__notify_launch_server('Invalid process stop server: "{}". He is still running'.format(
                server), btn_start, btn_stop, grpb, True)
        elif not result:
            self.__notify_launch_server('Server: "{}" is aborted. Result of job: {}'.format(
                server, result), btn_start, btn_stop, grpb, False)
        else:
            self.__notify_launch_server('Server successfully stop: "{}"'.format(server), btn_start, btn_stop, grpb,
                                        False)

    def stop_server(self, server):
        if server:
            server.stop()

    def parse_values_of_form(self):
        dict_values_work_ak = {}
        is_include_techno_ak, is_answer_with_type_cmd = True, True

        if not is_answer_with_type_cmd:
            dict_values_work_ak['BSB'] = self.ui.spinBox_BSB.value()
            dict_values_work_ak['R_W'] = self.ui.spinBox_R_W.value()
            dict_values_work_ak['OM'] = self.ui.spinBox_OM.value()

        if not self.ui.checkBox_Replace_Betta.isChecked():
            dict_values_work_ak['not_replace_betta'] = True

        # Рабочий АК
        dict_values_work_ak['betta_degree'] = self.ui.doubleSpinBox_Betta.value()
        dict_values_work_ak['readiness'] = self.ui.spinBox_Readhiness.value()
        dict_values_work_ak['RPon'] = self.ui.spinBox_RPon.value()
        dict_values_work_ak['ZPst'] = self.ui.spinBox_ZPst.value()
        dict_values_work_ak['OPst'] = self.ui.spinBox_OPst.value()
        dict_values_work_ak['LockDv'] = self.ui.spinBox_LockDv.value()
        dict_values_work_ak['ROP'] = self.ui.spinBox_ROP.value()
        dict_values_work_ak['KZOB'] = self.ui.spinBox_KZ_OB.value()
        dict_values_work_ak['Mode'] = self.ui.spinBox_Mode.value()
        dict_values_work_ak['AKA_IP4'] = self.ui.spinBox_AKA_IP4.value()
        dict_values_work_ak['AKA_IP3'] = self.ui.spinBox_AKA_IP3.value()
        dict_values_work_ak['AKA_IP2'] = self.ui.spinBox_AKA_IP2.value()
        dict_values_work_ak['AKA_IP1'] = self.ui.spinBox_AKA_IP1.value()

        dict_values_techno_ak = {}
        self.sig_reply_req_values_form.emit(dict_values_work_ak)
        self.log.warning('Warning')
        return

    def add_log_from(self, dict_values_ak, list_values_ak_keys, list_values_ak_title_rus, num):
        fmt_str = str(self.udp_server.get_prefix_recv) + " [" + str(num) + "]" + ": "
        # fmt_str = u" [" + unicode(num) + u"]" + u": "
        for i, v in enumerate(list_values_ak_keys):
            fmt_str += str(list_values_ak_title_rus[i]) + "={" + str(i) + "}, "
        fmt_str += "\n"
        list_values = []
        for x in list_values_ak_keys:
            list_values.append(dict_values_ak.get(x))
        try:
            fmt_str = fmt_str.format(*list_values)
        except Exception as e:
            print('Error format: ' + e.message)

        self.ui.plainTextEdit_log.appendPlainText(fmt_str)

    def add_on_table(self, dict_values_ak, list_values_ak_title, list_values_ak_title_rus):
        self.model_log.setHorizontalHeaderLabels(list_values_ak_title_rus)
        row = []
        for var in list_values_ak_title:
            value = dict_values_ak.get(var)
            item = QStandardItem(str(value))
            item.setEditable(False)
            row.append(item)

        self.model_log.appendRow(row)
        self.ui.tableView.setModel(self.model_log)
        self.ui.tableView.resizeColumnsToContents()
        self.ui.tableView.scrollToBottom()
        return self.model_log.rowCount()

    def add_log(self, fmt_str):
        fmt_str = self.pattern_log.sub(self.repl_str, fmt_str.replace('<', '&lt;').replace('>', '&gt;'))
        html_text = '<font color="Black" size=3 family="Times New Roman"><pre>{}</pre></font>'.format(fmt_str)
        self.ui.plainTextEdit_log.appendHtml(html_text)

    def add_log_err(self, fmt_str):
        fmt_str = fmt_str.replace('<', '&lt;').replace('>', '&gt;')
        html_text = '<font color="Red" size=4 family="Times New Roman"><pre><b>{}</b></pre></font>'.format(fmt_str)
        self.ui.plainTextEdit_log.appendHtml(html_text)

    def __notify_launch_server(self, text, btn_start, btn_stop, grb_control, server_is_running):
        self.log.info(text)
        grb_control.setEnabled(not server_is_running)
        btn_start.setEnabled(not server_is_running)
        btn_stop.setEnabled(server_is_running)
        if server_is_running:
            btn_start.setStyleSheet('background-color: rgb(0, 255, 0);')
            btn_stop.setStyleSheet('')
        else:
            btn_stop.setStyleSheet('background-color: rgb(255, 0, 0);')
            btn_start.setStyleSheet('')


def start_server_gui(logger, params, settings_conf, file_conf):
    app = QtGui.QApplication(sys.argv)
    form = MainForm(logger, params, settings_conf, file_conf)
    form.show()
    sys.exit(app.exec_())
