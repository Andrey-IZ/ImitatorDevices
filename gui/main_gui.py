import copy
import re
import sys

from PyQt4 import QtGui, uic
from PyQt4.Qt import *

from gui.gui_tools.table_clients.update_table_client import ModelNetClients
from imitator_device.interfaces.serial.ServerSerialDeviceImitator import serial_server_start, ServerSerialDeviceimitator
from imitator_device.interfaces.socket.ServerSocketDeviceImitator import socket_server_start, ServerSocketDeviceimitator
from gui.gui_tools.gui_protocol import GuiProtocol
from gui.gui_tools.reload_gui import GuiReload, GuiControlsReload
from gui.main_window_ui import Ui_MainWindow
from gui.qt_logging import XStream


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
        self.__is_init_server = True
        self.settings_conf = settings_conf
        self.params = params
        self.model_net_clients = ModelNetClients(self.ui.tableView_NetClients)
        self.__pattern_log_str = re.compile(r'(<.*?>[^<]+?)(".*?")', re.DOTALL)
        self.__pattern_log_apostr = re.compile(r'(\'.*?\')', re.DOTALL)
        self.__pattern_log_digit_msg = re.compile(r'(?<=[\W\s])((?:[0-9]+)|(?:[0-9A-F]{2})|(?:[0-9A-F]{4}))(?=[\W\s])')
        self.__pattern_log_bool_msg = re.compile(r'(?<=[\W\s])((?:true)|(?:false))(?=[\W\s])', re.I)
        self.__pattern_log_msg_text = re.compile(
            r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d{3} &lt;[A-Z]&gt;'
            r' \[\w+~.*?\]\s)(.*)', re.I | re.DOTALL)
        self.__pattern_log = re.compile(
            r'(?P<date>\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d{3}) &lt;(?P<msg>[A-Z])&gt;'
            r' \[(?P<log_name>\w+)~(?P<thread_name>.*?)\]\s.*?', re.I | re.M)
        self.repl_str = r'<font color=gray>\g<date></font> &lt;<font color=red>\g<msg></font>&gt;' \
                        r' [<U>\g<log_name></U>~<font color="darkblue"><U>\g<thread_name></U></font>] '

        # XStream.stderr().messageWritten.connect(self.add_log_err)
        XStream.stdout().messageWritten.connect(self.add_log)

        self.__init_config()
        self.__init_connect()

    def __init_config(self):
        self.gui_protocol = GuiProtocol(self.log, self)
        gui_controls_reload = GuiControlsReload()
        gui_controls_reload.gui_protocol = self.gui_protocol
        gui_controls_reload.file_config = self.file_conf
        gui_controls_reload.params_console = self.params
        gui_controls_reload.settings_conf = self.settings_conf
        gui_controls_reload.is_init_server = self.__is_init_server
        gui_controls_reload.fill_control_param.update(
            {'socket': (self.ui.spinBox_Port_Bind, self.ui.lineEditIpAddressBind)})
        gui_controls_reload.fill_control_param.update({'serial': (self.ui.comboBox_ListPorts, self.ui.comboBox_BaudRate,
                                                                  self.ui.comboBox_DataBits, self.ui.comboBox_StopBits,
                                                                  self.ui.comboBox_Parity)})
        self.gui_reload = GuiReload(self.log, gui_controls_reload)
        self.gui_reload.sig_status_thread.connect(self.__set_btn_reload)
        self.gui_reload.sig_status_thread.connect(self.__set_enable_form)
        self.gui_reload.sig_job_finished.connect(self.__rebuild_frame)
        self.gui_reload.sig_job_finished.connect(self.__reset_highlight)
        self.gui_reload.sig_start_new_job.connect(self.__init_servers)
        self.gui_reload.start()

    def __rebuild_frame(self, status):
        if status:
            self.gui_protocol.build_form()

    def __init_servers(self):
        if self.__is_init_server:
            settings_conf = self.settings_conf
            if settings_conf.socket_settings.host:
                socket_logger = copy.copy(self.log)
                socket_logger.name = settings_conf.socket_settings.socket_type_str
                if self.gui_reload.isFinished():
                    self.server_socket = socket_server_start(settings_conf, socket_logger,
                                                             self.gui_protocol.get_control_form())
                    btn_start, btn_stop, grpb = self.ui.pushButtonStartNet, self.ui.pushButtonStopNet, self.ui.groupBox_Net
                    self.__notify_launch_server('server stopped: "{}"'.format(self.server_socket, str(
                        self.server_socket.get_address())), btn_start, btn_stop, grpb, False)
                    if self.server_socket:
                        self.__notify_launch_server('server start: "{}"'.format(self.server_socket, str(
                            self.server_socket.get_address())), btn_start, btn_stop, grpb, True)
            else:
                self.ui.dockWidget_Net.setVisible(False)
            if settings_conf.serialport_settings.port:
                btn_start, btn_stop, grpb = self.ui.pushButtonStart_Serial, self.ui.pushButtonStop_Serial, self.ui.groupBox_Serial
                serial_logger = copy.copy(self.log)
                serial_logger.name = 'Serial'
                self.server_serial = serial_server_start(settings_conf, serial_logger,
                                                         self.gui_protocol.get_control_form())
                if self.server_serial:
                    self.__notify_launch_server('server start: "{}"'.format(self.server_serial, str(
                        self.server_serial.get_address())), btn_start, btn_stop, grpb, True)
            else:
                self.ui.dockWidget_Serial.setVisible(False)

            if self.server_socket:
                self.server_socket.sig_client_added.connect(self.model_net_clients.add_row)
                self.server_socket.sig_client_removed.connect(self.model_net_clients.del_row)
                self.server_socket.sig_job_finished.connect(self.suddenly_stop_server)
                self.ui.pushButtonStopNet.clicked.connect(lambda: self.stop_server(self.server_socket))
            else:
                self.ui.tableView_NetClients.setVisible(False)
                self.ui.label_CountClientNet.setVisible(False)
            if self.server_serial:
                self.server_serial.sig_job_finished.connect(self.suddenly_stop_server)
                self.ui.pushButtonStop_Serial.clicked.connect(lambda: self.stop_server(self.server_serial))

    def __add_table_net_clients(self, client_name):
        self.model_net_clients.add_row(client_name)

    def __reset_highlight(self):
        self._set_highlight_button(self.ui.pushButtonReloadConfig)

    def __init_connect(self):
        self.ui.pushButtonReloadConfig.clicked.connect(self.__reload_config)
        self.ui.pushButtonStartNet.clicked.connect(self.start_net_server)
        self.ui.pushButtonStart_Serial.clicked.connect(self.start_serial_server)

        # if self.server_socket:
        #     self.server_socket.sig_count_client_changed.connect(lambda n: self.ui.spinBox_Count_Connections.setValue(n))
        #     self.server_socket.sig_job_finished.connect(self.suddenly_stop_server)
        #     self.server_socket.sig_count_client_changed.connect()
        #     self.ui.pushButtonStopNet.clicked.connect(lambda: self.stop_server(self.server_socket))
        # else:
        #     self.ui.spinBox_Count_Connections.setVisible(False)
        #     self.ui.label_CountClientNet.setVisible(False)
        # if self.server_serial:
        #     self.server_serial.sig_job_finished.connect(self.suddenly_stop_server)
        #     self.ui.pushButtonStop_Serial.clicked.connect(lambda: self.stop_server(self.server_serial))

    def __reload_config(self):
        if hasattr(self, 'gui_protocol'):
            self.gui_protocol.remove_all()
        # if self.server_socket:
        #     self.stop_server(self.server_socket)
        # if self.server_serial:
        #     self.stop_server(self.server_serial)

        self.__is_init_server = False
        self.gui_reload.controls_reload.is_init_server = self.__is_init_server
        self.gui_reload.start()

    def __init_connect_server(self, server):
        if server:
            # self.ui.spinBox_BSB.valueChanged.connect(server.slot_values_form_changed)
            pass

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
        except Exception as err:
            print('Error format: {}', err)

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
        fmt_str = '<font color="Black">' + fmt_str.replace('<', '&lt;').replace('>', '&gt;') + '</font>'
        m = self.__pattern_log_msg_text.search(fmt_str)
        if m:
            msg_text = m.group(2)
            if msg_text:
                repl_text = self.__pattern_log_digit_msg.sub(
                    '<font color=#0000FF size=3 family="Times New Roman">\g<1></font>', msg_text)
                fmt_str = self.__pattern_log_msg_text.sub('\g<1>' + repl_text, fmt_str)
        fmt_str = self.__pattern_log_str.sub(
            '\g<1><font color=#CC6A00 size=3 family="Times New Roman"><b>\g<2></b></font>', fmt_str)
        fmt_str = self.__pattern_log_bool_msg.sub(
            '<font color=#0000AA size=3 family="Times New Roman"><b>\g<1></b></font>', fmt_str)
        fmt_str = self.__pattern_log_apostr.sub('<font color=#009A00 size=3 family="Times New Roman">\g<1></font>',
                                                fmt_str)
        fmt_str = self.__pattern_log.sub(self.repl_str, fmt_str)
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
            self._set_highlight_button(btn_start, True)
            self._set_highlight_button(btn_stop, None)
        else:
            self._set_highlight_button(btn_stop, False)
            self._set_highlight_button(btn_start, None)

    def __set_btn_reload(self, status):
        if status is None:
            status = False
        self._set_highlight_button(self.ui.pushButtonReloadConfig, status)

    @staticmethod
    def _set_highlight_button(button, status=None):
        if status:
            button.setStyleSheet('background-color: rgb(0, 255, 0);')
        elif status is None:
            button.setStyleSheet('')
        else:
            button.setStyleSheet('background-color: rgb(255, 0, 0);')

    def __set_enable_form(self, is_enabled):
        self.ui.pushButtonReloadConfig.setEnabled(bool(is_enabled))
        # self.ui.centralwidget.setEnabled(is_enabled)


def start_server_gui(logger, params, settings_conf, file_conf):
    app = QtGui.QApplication(sys.argv)
    form = MainForm(logger, params, settings_conf, file_conf)
    form.show()
    sys.exit(app.exec_())
