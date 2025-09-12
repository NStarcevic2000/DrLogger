from PyQt5.QtWidgets import QTableView, QAbstractItemView
from PyQt5.QtCore import QAbstractTableModel, Qt, QVariant
from PyQt5.QtGui import QColor, QStandardItemModel, QStandardItem

from pandas import DataFrame

from util.config_store import ConfigManager as CfgMan
from util.logs_manager import LogsManager
from util.logs_column import PREDEFINED_COLUMN_NAMES as PCN
from processor.processor_manager import ProcessorManager


class LogsTableModel(QAbstractTableModel):
    def __init__(self,
                 visible_data: DataFrame,
                 metadata: DataFrame):
        super().__init__()
        self._visible_data = visible_data
        self._metadata = metadata

    def rowCount(self, parent=None):
        return len(self._visible_data)

    def columnCount(self, parent=None):
        return len(self._visible_data.columns)

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid() or index.row() >= self.rowCount() or index.column() >= self.columnCount():
            return QVariant()
        if role == Qt.DisplayRole:
            return str(self._visible_data.iloc[index.row(), index.column()])
        elif role == Qt.ForegroundRole and PCN.FOREGROUND.value in self._metadata.columns:
            fg = self._metadata.iloc[index.row()][PCN.FOREGROUND.value] if PCN.FOREGROUND.value in self._metadata.columns else None
            if fg:
                return QColor(fg)
            else:
                return QColor("black")
        elif role == Qt.BackgroundRole and PCN.BACKGROUND.value in self._metadata.columns:
            bg = self._metadata.iloc[index.row()][PCN.BACKGROUND.value] if PCN.BACKGROUND.value in self._metadata.columns else None
            if bg:
                return QColor(bg)
            else:
                return QColor("white")
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
        
        self.cached_prerendered_data:DataFrame = DataFrame()
        self.cached_prerendered_metadata:DataFrame = DataFrame()
        self.cached_visible_data:DataFrame = DataFrame()
        self.cached_metadata:DataFrame = DataFrame()

    def refresh(self,
            preview_lines: int | None = None,
            specific_rows: list[int] | None = None,
            show_collapsed: bool = False):
        ProcessorManager().run()
        self.setUpdatesEnabled(False)
        self.setModel(
            LogsTableModel(
                *LogsManager().get_data(
                    rows=preview_lines if specific_rows is None else specific_rows,
                    show_collapsed=show_collapsed
                ),
            )
        )
        self.resizeColumnsToContents()
        # Last column does not expand indefinitely; horizontal scrolling enabled
        self.setHorizontalScrollMode(QAbstractItemView.ScrollPerPixel)
        self.horizontalHeader().setStretchLastSection(True)
        self.setUpdatesEnabled(True)

    def get_search_indexes(self, search_text: str, in_collapsed_data: bool=False) -> list[int]:
        indexes = []
        data = LogsManager().get_data(show_collapsed=in_collapsed_data)[0]
        for row in range(len(data)):
            for col in data.columns:
                if search_text.lower() in str(data.at[row, col]).lower():
                    indexes.append(row)
                    break
        return indexes
