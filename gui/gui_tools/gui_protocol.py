from libs.log_tools.logger import Logger
import copy
from PyQt4 import QtGui, QtCore

KW_PAGES, KW_GROUPS, KW_FIELDS, KW_GUI_MANUAL_ANSWER, KW_GUI_PAGES = (
    'pages', 'groups', 'fields', 'manual_answer', 'pages')
KW_GUI_REF, KW_GUI_NAME, KW_GUI_CONTROL_TYPE, KW_GUI_ROW, KW_GUI_COLUMN, KW_GUI_ROWSPAN, KW_GUI_COLSPAN, KW_GUI_DEFAULT, \
KW_GUI_DATA, KW_GUI_SB_DIGIT = (
    'ref', 'name', 'control_type', 'row', 'column', 'rowspan', 'colspan', 'default', 'data', 'digit')
KW_HANDLER_CONNECT, KW_MODULE_NAME, KW_FUNCTION_NAME = ('handler_connect', 'module_name', 'function_name')
KW_FIELD_SPINBOX, KW_FIELD_CHECKBOX, KW_FIELD_COMBOBOX = ('spinbox', 'checkbox', 'combobox')
KW_GUI_SPINBOX_MAX_VALUE, KW_GUI_SPINBOX_MIN_VALUE, KW_GUI_SPINBOX_STEP = ('max_value', 'min_value', 'sb_step')
KW_GUI_HLAYOUT, KW_GUI_VLAYOUT = ('h_layout', 'v_layout')
CHLIST_CONTROL_TYPE = {KW_FIELD_SPINBOX, KW_FIELD_CHECKBOX, KW_FIELD_COMBOBOX}
CHLIST_REQ_GUI = (KW_PAGES, KW_GROUPS, KW_FIELDS)
CHLIST_REQ_FIELDS = {KW_GUI_ROWSPAN, KW_GUI_COLSPAN,
                     KW_GUI_NAME, KW_GUI_CONTROL_TYPE, KW_GUI_NAME, KW_GUI_ROW, KW_GUI_COLUMN, KW_GUI_DEFAULT}
CHLIST_REQ_MANUAL_ANSWER = {KW_GUI_NAME, KW_HANDLER_CONNECT}
CHLIST_REQ_MA_CONNECT = {KW_MODULE_NAME, KW_FUNCTION_NAME}
CHLIST_REQ_GROUP = {KW_GUI_NAME, KW_GUI_ROW, KW_GUI_COLUMN, KW_GUI_ROWSPAN, KW_GUI_COLSPAN}


class ControlGuiValues(object):
    def __init__(self, dict_gui_ctrl, window):
        self.__dict_gui_ctrl = dict_gui_ctrl
        self.__window = window

    def set_ui_value(self, page, group, name, ctrl_type, value):
        try:
            fields = self.__dict_gui_ctrl.get(page).get(KW_GROUPS).get(group).get(KW_FIELDS)
            for field in fields:
                if fields[field].get(KW_GUI_CONTROL_TYPE) == ctrl_type:
                    if ctrl_type == KW_FIELD_SPINBOX:
                        fields[field].get(KW_GUI_REF)[0].setValue(value)
                    if ctrl_type == KW_FIELD_CHECKBOX:
                        fields[field].get(KW_GUI_REF)[0].setChecked(value)
                    if ctrl_type == KW_FIELD_COMBOBOX:
                        fields[field].get(KW_GUI_REF)[0].setCurrentIndex(value)
        except Exception as err:
            raise ValueError(
                '!ERROR: on function get_ui_value: param= {}, {}, {}, {}; ({});'.format(
                    fields[field], page, group, name, ctrl_type)) from err

    def get_ui_value(self, page, group, name, ctrl_type):
        fields = {}
        try:
            fields = self.__dict_gui_ctrl.get(page).get(KW_GROUPS).get(group).get(KW_FIELDS)
            for field in fields:
                if fields[field].get(KW_GUI_CONTROL_TYPE) == ctrl_type:
                    if ctrl_type == KW_FIELD_SPINBOX:
                        return fields[field].get(KW_GUI_REF)[0].value()
                    if ctrl_type == KW_FIELD_CHECKBOX:
                        return fields[field].get(KW_GUI_REF)[0].isChecked()
                    if ctrl_type == KW_FIELD_COMBOBOX:
                        return fields[field].get(KW_GUI_REF)[0].currentIndex()
        except Exception as err:
            raise ValueError(
                '!ERROR: on function get_ui_value: param= {}, {}, {}, {}; ({});'.format(
                    fields[field], page, group, name, ctrl_type)) from err


class GuiProtocol(object):
    def __init__(self, logger, main_window):
        self.__window = main_window
        self.__log = logger
        self.__dict_gui_ctrl = {}
        self.__default_field_dict_spinbox = {KW_GUI_NAME: 'spinbox', KW_GUI_ROW: 0, KW_GUI_COLUMN: 0, KW_GUI_REF: None,
                                             KW_GUI_COLSPAN: 1, KW_GUI_ROWSPAN: 1, KW_GUI_DEFAULT: 0, KW_GUI_SB_DIGIT: 0,
                                             KW_GUI_SPINBOX_MAX_VALUE: 100, KW_GUI_SPINBOX_MIN_VALUE: 0}
        self.__default_field_dict_checkbox = {KW_GUI_NAME: 'checkbox', KW_GUI_ROW: 0, KW_GUI_COLUMN: 0,
                                              KW_GUI_REF: None,
                                              KW_GUI_COLSPAN: 1, KW_GUI_ROWSPAN: 1, KW_GUI_DEFAULT: False}
        self.__default_field_dict_combobox = {KW_GUI_NAME: 'combobox', KW_GUI_ROW: 0, KW_GUI_COLUMN: 0,
                                              KW_GUI_REF: None,
                                              KW_GUI_COLSPAN: 1, KW_GUI_ROWSPAN: 1, KW_GUI_DEFAULT: 0, KW_GUI_DATA: []}
        self.__default_group_dict = {KW_GUI_NAME: 'group', KW_GUI_ROW: 0, KW_GUI_COLUMN: 0,
                                     KW_GUI_COLSPAN: 1, KW_GUI_ROWSPAN: 1, KW_FIELDS: [], KW_GUI_REF: None}
        self.__default_page_dict = {KW_GUI_NAME: 'page1', KW_GROUPS: [], KW_GUI_REF: None}
        self._add_tabs('Страницы протокола')

    @property
    def logger(self) -> Logger:
        return self.__log

    @logger.setter
    def logger(self, value):
        self.__log = value

    def _validate(self, dict_gui_property):
        kw_gui = set(dict_gui_property).difference(CHLIST_REQ_GUI)
        if not kw_gui or kw_gui != {KW_GUI_MANUAL_ANSWER}:
            raise ValueError('!ERROR: <GUI> Found invalid keywords: "{}" into GUI'.format(kw_gui))
        if dict_gui_property.get(KW_PAGES) and not isinstance(dict_gui_property.get(KW_PAGES), str):
            raise ValueError('!ERROR: <GUI> keyword "{}" is not type of str'.format(KW_PAGES))
        if not (dict_gui_property.get(KW_GROUPS) and
                        set(dict_gui_property.get(KW_GROUPS)).difference(CHLIST_REQ_GROUP) == set()):
            raise ValueError('!ERROR: <GUI> Found not all keywords of group')
        if not (dict_gui_property.get(KW_FIELDS) and
                        set(dict_gui_property.get(KW_FIELDS)[0].keys()).difference(CHLIST_REQ_FIELDS) == set()):
            raise ValueError('!ERROR: <GUI> Found not all keywords of fields')
        if not (set(dict_gui_property.get(KW_GUI_MANUAL_ANSWER)).difference(CHLIST_REQ_MANUAL_ANSWER) == set()):
            raise ValueError('!ERROR: <GUI> Found not all keywords of manual answer')

    def append(self, dict_gui_property):
        # self._validate(dict_gui_property)
        for page in dict_gui_property.get(KW_PAGES, []):
            dict_page = copy.copy(self.__default_page_dict)
            dict_page.update(page)
            _page_dict = {}
            _page = self._add_page(dict_page)
            _page_dict[KW_GUI_REF] = _page[0]
            _page_dict[KW_GUI_HLAYOUT] = _page[1]
            _page_dict[KW_GUI_VLAYOUT] = _page[2]

            dict_group = {}
            for group in dict_page.get(KW_GROUPS, []):
                copy_group = copy.copy(self.__default_group_dict)
                copy_group.update(group)
                _groupbox = self._add_groupbox(_page, copy_group)
                list_field = {}
                for field in copy_group.get(KW_FIELDS, []):
                    if field.get(KW_GUI_CONTROL_TYPE) == KW_FIELD_SPINBOX:
                        copy_field = copy.copy(self.__default_field_dict_spinbox)
                        copy_field.update(field)
                        copy_field[KW_GUI_REF] = self._add_spinbox(_groupbox, copy_field)
                    elif field.get(KW_GUI_CONTROL_TYPE) == KW_FIELD_CHECKBOX:
                        copy_field = copy.copy(self.__default_field_dict_checkbox)
                        copy_field.update(field)
                        copy_field[KW_GUI_REF] = self._add_checkbox(_groupbox, copy_field)
                    elif field.get(KW_GUI_CONTROL_TYPE) == KW_FIELD_COMBOBOX:
                        copy_field = copy.copy(self.__default_field_dict_combobox)
                        copy_field.update(field)
                        copy_field[KW_GUI_REF] = self._add_combobox(_groupbox, copy_field)

                    list_field[copy_field.get(KW_GUI_NAME)] = copy_field
                self._post_groupbox(_groupbox)
                copy_group[KW_FIELDS] = list_field
                dict_group[copy_group.get(KW_GUI_NAME)] = copy_group

            _page_dict[KW_GROUPS] = dict_group
            self.__dict_gui_ctrl[dict_page.get(KW_GUI_NAME)] = _page_dict

    def _post_groupbox(self, groupbox):
        groupbox, horizontal_group, vertical_group = groupbox
        spacer_vertical = QtGui.QSpacerItem(20, 0, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        vertical_group.addSpacerItem(spacer_vertical)
        spacer_horizontal = QtGui.QSpacerItem(20, 0, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        horizontal_group.addSpacerItem(spacer_horizontal)

    def _add_tabs(self, tab_name):
        cw = self.__window.ui.centralwidget
        self._tabs = QtGui.QTabWidget(cw)
        centralLayout = QtGui.QVBoxLayout(cw)
        centralLayout.setObjectName("verticalLayout")
        # sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Expanding)
        # sizePolicy.setHorizontalStretch(0)
        # sizePolicy.setVerticalStretch(0)
        # sizePolicy.setHeightForWidth(self._tabs.sizePolicy().hasHeightForWidth())
        # self._tabs.setSizePolicy(sizePolicy)
        self._tabs.setMinimumSize(QtCore.QSize(965, 0))
        self._tabs.setObjectName("tabWidget")

        centralLayout.addWidget(self._tabs, 0)

    def _add_page(self, dict_page) -> tuple:
        tab = QtGui.QWidget()
        vertical = QtGui.QVBoxLayout(tab)
        page_name = dict_page.get(KW_GUI_NAME)
        tab.setObjectName(page_name)
        self._tabs.addTab(tab, page_name)
        self._tabs.setTabText(self._tabs.indexOf(tab), page_name)

        horizontal = QtGui.QHBoxLayout()
        vertical.addLayout(horizontal, 0)
        return tab, horizontal, vertical

    def _add_groupbox(self, page, dict_groupbox):
        tab, horizontal_page, vertical_page = page
        groupbox = QtGui.QGroupBox(tab)
        groupbox.setTitle(dict_groupbox.get(KW_GUI_NAME))
        vertical_group = QtGui.QVBoxLayout(groupbox)
        horizontal_group = QtGui.QHBoxLayout()
        vertical_group.addLayout(horizontal_group, 0)

        horizontal_page.addWidget(groupbox)
        return groupbox, horizontal_group, vertical_group

    def _add_spinbox(self, groupbox, dict_spinbox):
        groupbox, horizontal_group, vertical_group = groupbox
        spinbox = QtGui.QDoubleSpinBox(groupbox)
        spinbox.setDecimals(dict_spinbox.get(KW_GUI_SB_DIGIT))
        spinbox.setValue(dict_spinbox.get(KW_GUI_DEFAULT))
        label = QtGui.QLabel(groupbox)
        label.setText(dict_spinbox.get(KW_GUI_NAME))

        horizontal_sb = QtGui.QHBoxLayout()
        horizontal_sb.addWidget(label)
        horizontal_sb.addWidget(spinbox)

        horizontal_group.addLayout(horizontal_sb, 0)
        return spinbox, horizontal_sb

    def _add_checkbox(self, groupbox, dict_checkbox):
        groupbox, horizontal_group, vertical_group = groupbox
        checkbox = QtGui.QCheckBox(groupbox)
        checkbox.setChecked(dict_checkbox.get(KW_GUI_DEFAULT))
        label = QtGui.QLabel(groupbox)
        label.setText(dict_checkbox.get(KW_GUI_NAME))

        horizontal_cb = QtGui.QHBoxLayout()
        horizontal_cb.addWidget(checkbox)
        horizontal_cb.addWidget(label)
        print("==============")
        horizontal_group.addLayout(horizontal_cb, 0)
        return checkbox, horizontal_cb

    def _add_combobox(self, groupbox, dict_combobox):
        groupbox, horizontal_group, vertical_group = groupbox
        combobox = QtGui.QComboBox(groupbox)
        combobox.addItems(dict_combobox.get(KW_GUI_DATA))
        combobox.setCurrentIndex(dict_combobox.get(KW_GUI_DEFAULT))

        label = QtGui.QLabel(groupbox)
        label.setText(dict_combobox.get(KW_GUI_NAME))

        horizontal_cb = QtGui.QHBoxLayout()
        horizontal_cb.addWidget(label)
        horizontal_cb.addWidget(combobox)

        rowspan = dict_combobox.get(KW_GUI_ROWSPAN)
        rowspan -= 1
        if rowspan > 0:
            dict_combobox[KW_GUI_ROWSPAN] = rowspan
            horizontal_group_new = QtGui.QHBoxLayout(groupbox)
            horizontal_group.addLayout(horizontal_cb)
            vertical_group.addLayout(horizontal_group_new)
        else:
            horizontal_group.addLayout(horizontal_cb, 0)
        return combobox, horizontal_cb

    def get_control_form(self) -> ControlGuiValues:
        return ControlGuiValues(self.__dict_gui_ctrl, self.__window)
