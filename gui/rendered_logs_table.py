from PyQt5.QtWidgets import QTableView, QAbstractItemView
from PyQt5.QtCore import QAbstractTableModel, Qt, QVariant
from PyQt5.QtGui import QColor, QStandardItemModel, QStandardItem

from pandas import DataFrame, Series

from util.config_store import ConfigManager as CfgMan
from logs_managing.logs_manager import LogsManager
from logs_managing.logs_column_types import RESERVED_COLUMN_NAMES_NAMESPACE as RColNameNS
from processor.processor_manager import ProcessorManager


class LogsTableModel(QAbstractTableModel):
    ''' Table model for displaying logs with metadata support. 
        Should be used in conjunction with RenderedLogsTable(or any QTableView.setModel).\n
        Advise: Do not use directly, use RenderedLogsTable
    ''' 
    def __init__(self,
                 data: DataFrame=None,
                 metadata: Series[dict]=None,
                 colapsable: Series[tuple[DataFrame, DataFrame]]=None):
        super().__init__()
        self._visible_data = None
        self._metadata = None
        self._colapsable = None
        self.update_model_data(data, metadata, colapsable)

    def rowCount(self, parent=None):
        return len(self._visible_data)

    def columnCount(self, parent=None):
        return len(self._visible_data.columns)

    def data(self, index, role=Qt.DisplayRole):
        # Default model handling
        if not index.isValid() or index.row() >= self.rowCount() or index.column() >= self.columnCount():
            return QVariant()
        # Display role = simply cast to string
        if role == Qt.DisplayRole:
            return str(self._visible_data.iloc[index.row(), index.column()])
        # Foreground role = use metadata column if available
        elif role == Qt.ForegroundRole:
            fg = self._metadata.iloc[index.row()]["Foreground Color"] if "Foreground Color" in self._metadata.columns else None
            if fg:
                return QColor(fg)
            else:
                return QColor("#000000")
        # Background role = use metadata column if available
        elif role == Qt.BackgroundRole:
            bg = self._metadata.iloc[index.row()]["Background Color"] if "Background Color" in self._metadata.columns else None
            if bg:
                return QColor(bg)
            else:
                return QColor("#FFFFFF")
        # Text alignment role = left and vertically centered
        elif role == Qt.TextAlignmentRole:
            return Qt.AlignLeft | Qt.AlignVCenter
        return QVariant()
    
    # If the row is collapsed, show it
    def show_collapsed(self, rows:int|list[int]|None=None):
        if rows is None:
            rows = self._colapsable.index.tolist()
        elif isinstance(rows, int):
            if rows in self._colapsable.index:
                rows = [rows]
            else:
                raise ValueError(f"Row index {rows} out of range.")
        elif isinstance(rows, list):
            for r in rows:
                if r not in self._colapsable.index:
                    raise ValueError(f"Row index {r} out of range.")
        else:
            raise ValueError("Invalid row index type.")

        self.beginResetModel()
        for row in rows:
            self._visible_data.insert(row+1, self._colapsable.at[row][0])
            self._metadata.insert(row+1, self._colapsable.at[row][1])


        self.endResetModel()
    
    def hide_collapsed(self):
        self.beginResetModel()
        self._visible_data = self._visible_data[~self._metadata.get("Collapsed Rows", Series([False]*len(self._metadata))).astype(bool)].reset_index(drop=True)
        self._metadata = self._metadata[~self._metadata.get("Collapsed Rows", Series([False]*len(self._metadata))).astype(bool)].reset_index(drop=True)
        self.endResetModel()

    def update_model_data(self,
                    data: DataFrame,
                    metadata: Series[dict],
                    colapsable: Series[tuple[DataFrame, DataFrame]]):
        ''' Update the model with new data, metadata, and collapsable information.
            This will refresh the view automatically.
        '''
        self.beginResetModel()
        self._visible_data = data
        self._metadata = metadata
        self._colapsable = colapsable
        self.endResetModel()





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

        self.model = LogsTableModel()
        
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

    # def get_search_indexes(self, search_text: str, in_collapsed_data: bool=False) -> list[int]:
    #     indexes = []
    #     data = LogsManager().get_data(show_collapsed=in_collapsed_data)[0]
    #     for row in range(len(data)):
    #         for col in data.columns:
    #             if search_text.lower() in str(data.at[row, col]).lower():
    #                 indexes.append(row)
    #                 break
    #     return indexes
