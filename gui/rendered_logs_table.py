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
        if not index.isValid() or index.row() >= self.rowCount() or index.column() >= self.columnCount():
            return QVariant()
        if role == Qt.DisplayRole:
            return str(self._visible_data.iloc[index.row(), index.column()])
        elif role == Qt.ForegroundRole and "Foreground" in self._metadata.columns:
            fg = self._metadata.iloc[index.row()]["Foreground"] if "Foreground" in self._metadata.columns else None
            if fg:
                return QColor(fg)
            else:
                return QColor("black")
        elif role == Qt.BackgroundRole and "Background" in self._metadata.columns:
            bg = self._metadata.iloc[index.row()]["Background"] if "Background" in self._metadata.columns else None
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
            prerendered_data: bool = False,
            from_cache: bool = False):
        ProcessorManager().run()
        self.setUpdatesEnabled(False)
        if not from_cache or None in (self.cached_prerendered_data, self.cached_prerendered_metadata, self.cached_visible_data, self.cached_metadata):
            self.cached_prerendered_data = LogsManager().get_visible_data(rows=preview_lines)
            self.cached_prerendered_metadata = LogsManager().get_metadata(rows=preview_lines)
            self.cached_visible_data, self.cached_metadata = LogsManager().get_rendered_data(rows=preview_lines)
        if prerendered_data:
            self.setModel(
                LogsTableModel(
                    self.cached_prerendered_data.iloc[specific_rows] if specific_rows is not None else self.cached_visible_data,
                    self.cached_prerendered_metadata.iloc[specific_rows] if specific_rows is not None else self.cached_metadata
                )
            )
        else:
            self.setModel(
                LogsTableModel(
                    self.cached_visible_data.iloc[specific_rows] if specific_rows is not None else self.cached_visible_data,
                    self.cached_metadata.iloc[specific_rows] if specific_rows is not None else self.cached_metadata
                )
            )

        self.resizeColumnsToContents()
        # Last column does not expand indefinitely; horizontal scrolling enabled
        self.setHorizontalScrollMode(QAbstractItemView.ScrollPerPixel)
        self.horizontalHeader().setStretchLastSection(True)
        self.setUpdatesEnabled(True)
    
    def get_search_indexes(self, search_text: str, prerendered:bool=False) -> list[int]:
        indexes = []
        if prerendered:
            data = self.cached_prerendered_data
        else:
            data = self.cached_visible_data
        for row in range(len(data)):
            for col in data.columns:
                if search_text.lower() in str(data.at[row, col]).lower():
                    indexes.append(row)
                    break
        return indexes
