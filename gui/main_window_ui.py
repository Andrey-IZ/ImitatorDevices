# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'main_window.ui'
#
# Created by: PyQt4 UI code generator 4.11.4
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName(_fromUtf8("MainWindow"))
        MainWindow.resize(983, 800)
        self.centralwidget = QtGui.QWidget(MainWindow)
        self.centralwidget.setObjectName(_fromUtf8("centralwidget"))
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtGui.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 983, 21))
        self.menubar.setObjectName(_fromUtf8("menubar"))
        self.menu = QtGui.QMenu(self.menubar)
        self.menu.setObjectName(_fromUtf8("menu"))
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtGui.QStatusBar(MainWindow)
        self.statusbar.setObjectName(_fromUtf8("statusbar"))
        MainWindow.setStatusBar(self.statusbar)
        self.toolBar = QtGui.QToolBar(MainWindow)
        self.toolBar.setMouseTracking(True)
        self.toolBar.setAcceptDrops(True)
        self.toolBar.setObjectName(_fromUtf8("toolBar"))
        MainWindow.addToolBar(QtCore.Qt.TopToolBarArea, self.toolBar)
        self.dockWidget_Net = QtGui.QDockWidget(MainWindow)
        self.dockWidget_Net.setAutoFillBackground(False)
        self.dockWidget_Net.setFloating(False)
        self.dockWidget_Net.setFeatures(QtGui.QDockWidget.AllDockWidgetFeatures)
        self.dockWidget_Net.setObjectName(_fromUtf8("dockWidget_Net"))
        self.dockWidgetContents = QtGui.QWidget()
        self.dockWidgetContents.setObjectName(_fromUtf8("dockWidgetContents"))
        self.verticalLayout_10 = QtGui.QVBoxLayout(self.dockWidgetContents)
        self.verticalLayout_10.setObjectName(_fromUtf8("verticalLayout_10"))
        self.groupBox_Net = QtGui.QGroupBox(self.dockWidgetContents)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.groupBox_Net.sizePolicy().hasHeightForWidth())
        self.groupBox_Net.setSizePolicy(sizePolicy)
        self.groupBox_Net.setMinimumSize(QtCore.QSize(163, 0))
        self.groupBox_Net.setObjectName(_fromUtf8("groupBox_Net"))
        self.horizontalLayout_9 = QtGui.QHBoxLayout(self.groupBox_Net)
        self.horizontalLayout_9.setObjectName(_fromUtf8("horizontalLayout_9"))
        self.label_IP_4 = QtGui.QLabel(self.groupBox_Net)
        self.label_IP_4.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.label_IP_4.setObjectName(_fromUtf8("label_IP_4"))
        self.horizontalLayout_9.addWidget(self.label_IP_4)
        self.lineEditIpAddressBind = QtGui.QLineEdit(self.groupBox_Net)
        self.lineEditIpAddressBind.setMaximumSize(QtCore.QSize(100, 16777215))
        self.lineEditIpAddressBind.setMaxLength(15)
        self.lineEditIpAddressBind.setObjectName(_fromUtf8("lineEditIpAddressBind"))
        self.horizontalLayout_9.addWidget(self.lineEditIpAddressBind)
        self.spinBox_Port_Bind = QtGui.QSpinBox(self.groupBox_Net)
        self.spinBox_Port_Bind.setMaximumSize(QtCore.QSize(100, 16777215))
        self.spinBox_Port_Bind.setMinimum(1024)
        self.spinBox_Port_Bind.setMaximum(54000)
        self.spinBox_Port_Bind.setProperty("value", 11000)
        self.spinBox_Port_Bind.setObjectName(_fromUtf8("spinBox_Port_Bind"))
        self.horizontalLayout_9.addWidget(self.spinBox_Port_Bind)
        self.verticalLayout_10.addWidget(self.groupBox_Net)
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.pushButtonStartNet = QtGui.QPushButton(self.dockWidgetContents)
        self.pushButtonStartNet.setAutoFillBackground(False)
        self.pushButtonStartNet.setObjectName(_fromUtf8("pushButtonStartNet"))
        self.horizontalLayout.addWidget(self.pushButtonStartNet)
        self.pushButtonStopNet = QtGui.QPushButton(self.dockWidgetContents)
        self.pushButtonStopNet.setObjectName(_fromUtf8("pushButtonStopNet"))
        self.horizontalLayout.addWidget(self.pushButtonStopNet)
        self.verticalLayout_10.addLayout(self.horizontalLayout)
        self.dockWidget_Net.setWidget(self.dockWidgetContents)
        MainWindow.addDockWidget(QtCore.Qt.DockWidgetArea(4), self.dockWidget_Net)
        self.dockWidget_Output = QtGui.QDockWidget(MainWindow)
        self.dockWidget_Output.setFloating(False)
        self.dockWidget_Output.setFeatures(QtGui.QDockWidget.AllDockWidgetFeatures)
        self.dockWidget_Output.setObjectName(_fromUtf8("dockWidget_Output"))
        self.dockWidgetContents_2 = QtGui.QWidget()
        self.dockWidgetContents_2.setObjectName(_fromUtf8("dockWidgetContents_2"))
        self.verticalLayout_5 = QtGui.QVBoxLayout(self.dockWidgetContents_2)
        self.verticalLayout_5.setObjectName(_fromUtf8("verticalLayout_5"))
        self.plainTextEdit_log = QtGui.QPlainTextEdit(self.dockWidgetContents_2)
        self.plainTextEdit_log.setObjectName(_fromUtf8("plainTextEdit_log"))
        self.verticalLayout_5.addWidget(self.plainTextEdit_log)
        self.dockWidget_Output.setWidget(self.dockWidgetContents_2)
        MainWindow.addDockWidget(QtCore.Qt.DockWidgetArea(8), self.dockWidget_Output)
        self.dockWidget_Serial = QtGui.QDockWidget(MainWindow)
        self.dockWidget_Serial.setFloating(False)
        self.dockWidget_Serial.setObjectName(_fromUtf8("dockWidget_Serial"))
        self.dockWidgetContents_3 = QtGui.QWidget()
        self.dockWidgetContents_3.setObjectName(_fromUtf8("dockWidgetContents_3"))
        self.verticalLayout_11 = QtGui.QVBoxLayout(self.dockWidgetContents_3)
        self.verticalLayout_11.setObjectName(_fromUtf8("verticalLayout_11"))
        self.groupBox_Serial = QtGui.QGroupBox(self.dockWidgetContents_3)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.groupBox_Serial.sizePolicy().hasHeightForWidth())
        self.groupBox_Serial.setSizePolicy(sizePolicy)
        self.groupBox_Serial.setMinimumSize(QtCore.QSize(163, 0))
        self.groupBox_Serial.setObjectName(_fromUtf8("groupBox_Serial"))
        self.verticalLayout_7 = QtGui.QVBoxLayout(self.groupBox_Serial)
        self.verticalLayout_7.setObjectName(_fromUtf8("verticalLayout_7"))
        self.horizontalLayout_3 = QtGui.QHBoxLayout()
        self.horizontalLayout_3.setObjectName(_fromUtf8("horizontalLayout_3"))
        self.label_8 = QtGui.QLabel(self.groupBox_Serial)
        self.label_8.setObjectName(_fromUtf8("label_8"))
        self.horizontalLayout_3.addWidget(self.label_8)
        self.comboBox_ListPorts = QtGui.QComboBox(self.groupBox_Serial)
        self.comboBox_ListPorts.setMinimumSize(QtCore.QSize(100, 0))
        self.comboBox_ListPorts.setObjectName(_fromUtf8("comboBox_ListPorts"))
        self.horizontalLayout_3.addWidget(self.comboBox_ListPorts)
        self.label_9 = QtGui.QLabel(self.groupBox_Serial)
        self.label_9.setObjectName(_fromUtf8("label_9"))
        self.horizontalLayout_3.addWidget(self.label_9)
        self.comboBox_BaudRate = QtGui.QComboBox(self.groupBox_Serial)
        self.comboBox_BaudRate.setMinimumSize(QtCore.QSize(100, 0))
        self.comboBox_BaudRate.setObjectName(_fromUtf8("comboBox_BaudRate"))
        self.horizontalLayout_3.addWidget(self.comboBox_BaudRate)
        self.label_20 = QtGui.QLabel(self.groupBox_Serial)
        self.label_20.setObjectName(_fromUtf8("label_20"))
        self.horizontalLayout_3.addWidget(self.label_20)
        self.comboBox_DataBits = QtGui.QComboBox(self.groupBox_Serial)
        self.comboBox_DataBits.setMinimumSize(QtCore.QSize(100, 0))
        self.comboBox_DataBits.setObjectName(_fromUtf8("comboBox_DataBits"))
        self.horizontalLayout_3.addWidget(self.comboBox_DataBits)
        self.verticalLayout_7.addLayout(self.horizontalLayout_3)
        self.horizontalLayout_5 = QtGui.QHBoxLayout()
        self.horizontalLayout_5.setObjectName(_fromUtf8("horizontalLayout_5"))
        self.label_18 = QtGui.QLabel(self.groupBox_Serial)
        self.label_18.setObjectName(_fromUtf8("label_18"))
        self.horizontalLayout_5.addWidget(self.label_18)
        self.comboBox_Parity = QtGui.QComboBox(self.groupBox_Serial)
        self.comboBox_Parity.setMinimumSize(QtCore.QSize(100, 0))
        self.comboBox_Parity.setObjectName(_fromUtf8("comboBox_Parity"))
        self.horizontalLayout_5.addWidget(self.comboBox_Parity)
        self.label_19 = QtGui.QLabel(self.groupBox_Serial)
        self.label_19.setObjectName(_fromUtf8("label_19"))
        self.horizontalLayout_5.addWidget(self.label_19)
        self.comboBox_StopBits = QtGui.QComboBox(self.groupBox_Serial)
        self.comboBox_StopBits.setMinimumSize(QtCore.QSize(100, 0))
        self.comboBox_StopBits.setObjectName(_fromUtf8("comboBox_StopBits"))
        self.horizontalLayout_5.addWidget(self.comboBox_StopBits)
        self.verticalLayout_7.addLayout(self.horizontalLayout_5)
        self.verticalLayout_11.addWidget(self.groupBox_Serial)
        self.horizontalLayout_4 = QtGui.QHBoxLayout()
        self.horizontalLayout_4.setObjectName(_fromUtf8("horizontalLayout_4"))
        self.pushButtonStart_Serial = QtGui.QPushButton(self.dockWidgetContents_3)
        self.pushButtonStart_Serial.setAutoFillBackground(False)
        self.pushButtonStart_Serial.setObjectName(_fromUtf8("pushButtonStart_Serial"))
        self.horizontalLayout_4.addWidget(self.pushButtonStart_Serial)
        self.pushButtonStop_Serial = QtGui.QPushButton(self.dockWidgetContents_3)
        self.pushButtonStop_Serial.setObjectName(_fromUtf8("pushButtonStop_Serial"))
        self.horizontalLayout_4.addWidget(self.pushButtonStop_Serial)
        self.verticalLayout_11.addLayout(self.horizontalLayout_4)
        self.dockWidget_Serial.setWidget(self.dockWidgetContents_3)
        MainWindow.addDockWidget(QtCore.Qt.DockWidgetArea(4), self.dockWidget_Serial)
        self.dockWidget_Common = QtGui.QDockWidget(MainWindow)
        self.dockWidget_Common.setObjectName(_fromUtf8("dockWidget_Common"))
        self.dockWidgetContents_4 = QtGui.QWidget()
        self.dockWidgetContents_4.setObjectName(_fromUtf8("dockWidgetContents_4"))
        self.verticalLayout_3 = QtGui.QVBoxLayout(self.dockWidgetContents_4)
        self.verticalLayout_3.setObjectName(_fromUtf8("verticalLayout_3"))
        self.checkBox_Autoanswer = QtGui.QCheckBox(self.dockWidgetContents_4)
        self.checkBox_Autoanswer.setChecked(True)
        self.checkBox_Autoanswer.setObjectName(_fromUtf8("checkBox_Autoanswer"))
        self.verticalLayout_3.addWidget(self.checkBox_Autoanswer)
        self.pushButtonReloadConfig = QtGui.QPushButton(self.dockWidgetContents_4)
        self.pushButtonReloadConfig.setObjectName(_fromUtf8("pushButtonReloadConfig"))
        self.verticalLayout_3.addWidget(self.pushButtonReloadConfig)
        self.dockWidget_Common.setWidget(self.dockWidgetContents_4)
        MainWindow.addDockWidget(QtCore.Qt.DockWidgetArea(4), self.dockWidget_Common)
        self.dockWidget_LogCmd = QtGui.QDockWidget(MainWindow)
        self.dockWidget_LogCmd.setFloating(False)
        self.dockWidget_LogCmd.setObjectName(_fromUtf8("dockWidget_LogCmd"))
        self.dockWidgetContents_5 = QtGui.QWidget()
        self.dockWidgetContents_5.setObjectName(_fromUtf8("dockWidgetContents_5"))
        self.verticalLayout_6 = QtGui.QVBoxLayout(self.dockWidgetContents_5)
        self.verticalLayout_6.setObjectName(_fromUtf8("verticalLayout_6"))
        self.tableView = QtGui.QTableView(self.dockWidgetContents_5)
        self.tableView.setSelectionMode(QtGui.QAbstractItemView.SingleSelection)
        self.tableView.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        self.tableView.setObjectName(_fromUtf8("tableView"))
        self.verticalLayout_6.addWidget(self.tableView)
        self.dockWidget_LogCmd.setWidget(self.dockWidgetContents_5)
        MainWindow.addDockWidget(QtCore.Qt.DockWidgetArea(8), self.dockWidget_LogCmd)
        self.actionDebug = QtGui.QAction(MainWindow)
        self.actionDebug.setObjectName(_fromUtf8("actionDebug"))
        self.menu.addAction(self.actionDebug)
        self.menubar.addAction(self.menu.menuAction())

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(_translate("MainWindow", "Имитатор МУС200", None))
        self.menu.setTitle(_translate("MainWindow", "Справка", None))
        self.toolBar.setWindowTitle(_translate("MainWindow", "toolBar", None))
        self.dockWidget_Net.setWindowTitle(_translate("MainWindow", "Сеть", None))
        self.groupBox_Net.setTitle(_translate("MainWindow", "адрес приема данных", None))
        self.label_IP_4.setText(_translate("MainWindow", "IP = ", None))
        self.lineEditIpAddressBind.setInputMask(_translate("MainWindow", "000.000.000.000", None))
        self.lineEditIpAddressBind.setText(_translate("MainWindow", "127.0.0.1", None))
        self.pushButtonStartNet.setText(_translate("MainWindow", "Старт", None))
        self.pushButtonStopNet.setText(_translate("MainWindow", "Стоп", None))
        self.dockWidget_Output.setWindowTitle(_translate("MainWindow", "Вывод", None))
        self.dockWidget_Serial.setWindowTitle(_translate("MainWindow", "Com порт", None))
        self.groupBox_Serial.setTitle(_translate("MainWindow", "адрес приема данных", None))
        self.label_8.setText(_translate("MainWindow", "Порт", None))
        self.label_9.setText(_translate("MainWindow", "Скорость", None))
        self.label_20.setText(_translate("MainWindow", "Биты данных", None))
        self.label_18.setText(_translate("MainWindow", "Четность", None))
        self.label_19.setText(_translate("MainWindow", "Стопбит", None))
        self.pushButtonStart_Serial.setText(_translate("MainWindow", "Старт", None))
        self.pushButtonStop_Serial.setText(_translate("MainWindow", "Стоп", None))
        self.dockWidget_Common.setWindowTitle(_translate("MainWindow", "Общие", None))
        self.checkBox_Autoanswer.setText(_translate("MainWindow", "автоответ", None))
        self.pushButtonReloadConfig.setText(_translate("MainWindow", "Перезагрузить", None))
        self.dockWidget_LogCmd.setWindowTitle(_translate("MainWindow", "Журнла команд", None))
        self.actionDebug.setText(_translate("MainWindow", "Отладка", None))
        self.actionDebug.setShortcut(_translate("MainWindow", "F5", None))

