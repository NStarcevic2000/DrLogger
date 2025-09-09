from PyQt5.QtWidgets import QTableView, QAbstractItemView
from PyQt5.QtCore import QAbstractTableModel, Qt, QVariant
from PyQt5.QtGui import QColor, QStandardItemModel, QStandardItem

from pandas import DataFrame

from util.config_store import ConfigManager as CfgMan
from util.logs_manager import LogsManager
from processor.processor_manager import ProcessorManager


class LogsTableModel(QAbstractTableModel):
    def __init__(self,
                 visible_data: DataFrame,
                 metadata: DataFrame):
        super().__init__()
        self._visible_data = visible_data
        self._metadata = metadata

        self._collapsing_root_element = None

    def rowCount(self, parent=None):
        return len(self._visible_data)

    def columnCount(self, parent=None):
        return len(self._visible_data.columns)

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid():
            return QVariant()
        if role == Qt.DisplayRole:
            return str(self._visible_data.iloc[index.row(), index.column()])
        elif role == Qt.ForegroundRole and "Foreground" in self._metadata.columns:
            fg = self._metadata.at[index.row(), "Foreground"]
            if fg:
                return QColor(fg)
        elif role == Qt.BackgroundRole and "Background" in self._metadata.columns:
            bg = self._metadata.at[index.row(), "Background"]
            if bg:
                return QColor(bg)
        elif role == Qt.TextAlignmentRole:
            return Qt.AlignLeft | Qt.AlignVCenter
        return QVariant()

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                return str(self._visible_data.columns[section])
            else:
                return str(section)
        return QVariant()

class RenderedLogsTable(QTableView):
    def __init__(self):
        super().__init__()
        self.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.setSelectionMode(QAbstractItemView.SingleSelection)
        self.setSortingEnabled(False)
        self.setModel(LogsTableModel(DataFrame(), DataFrame()))
        self.setHorizontalScrollMode(QAbstractItemView.ScrollPerPixel)
        self.horizontalHeader().setStretchLastSection(True)

    def refresh(self, preview_lines: int | None = None):
        ProcessorManager().run()
        self.setUpdatesEnabled(False)
        self.setModel(
            LogsTableModel(
                *LogsManager().get_rendered_data(rows=preview_lines)
            )
        )
        self.resizeColumnsToContents()
        # Last column does not expand indefinitely; horizontal scrolling enabled
        self.setHorizontalScrollMode(QAbstractItemView.ScrollPerPixel)
        self.horizontalHeader().setStretchLastSection(True)
        self.setUpdatesEnabled(True)
