#!/usr/bin/env python
from PyQt5.QtGui import QStandardItemModel, QStandardItem


class ModelNetClients:
    def __init__(self, table_view):
        self._model_net_clients = QStandardItemModel(table_view)
        self._table_view = table_view

    @property
    def list_clients(self):
        return self._model_net_clients

    def _update(self):
        self._table_view.setModel(self._model_net_clients)
        self._table_view.resizeColumnsToContents()
        self._table_view.scrollToBottom()
        self._table_view.selectRow(self._model_net_clients.rowCount() - 1)
        self._table_view.setModel(self._model_net_clients)

    def add_row(self, row_str):
        item = QStandardItem(row_str)
        item.setEditable(False)
        self._model_net_clients.appendRow([item])
        self._update()

    def del_row(self, row_str):
        items = self._model_net_clients.findItems(row_str)
        if items:
             self._model_net_clients.removeRow(items[0].row())
             self._update()

    def clear(self):
        self._model_net_clients.clear()