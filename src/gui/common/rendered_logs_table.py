from PyQt5.QtWidgets import QTableView, QAbstractItemView
from PyQt5.QtCore import QAbstractTableModel, Qt, QVariant
from PyQt5.QtGui import QColor

from pandas import DataFrame, Series

from logs_managing.reserved_names import RESERVED_METADATA_NAMES as RMetaNS

class LogsTableModel(QAbstractTableModel):
    ''' Table model for displaying logs with metadata support. 
        Should be used in conjunction with RenderedLogsTable(or any QTableView.setModel).\n
        Advise: Do not use directly, use RenderedLogsTable
    ''' 
    def __init__(self,
                 data: DataFrame=None,
                 styles: Series=None):
        super().__init__()
        self._visible_data = None
        self._styles = None
        self.update_model_data(data, styles)

    def rowCount(self, _=None):
        return len(self._visible_data)

    def columnCount(self, _=None):
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
            if self._styles is None or index.row() < 0 or index.row() >= len(self._styles):
                return QColor("#000000")
            fg = self._styles.iloc[index.row()][RMetaNS.General.name][RMetaNS.General.ForegroundColor].get_value()
            if fg:
                return QColor(fg)
            else:
                return QColor("#000000")
        # Background role = use metadata column if available
        elif role == Qt.BackgroundRole:
            if self._styles is None or index.row() < 0 or index.row() >= len(self._styles):
                return QColor("#FFFFFF")
            bg = self._styles.iloc[index.row()][RMetaNS.General.name][RMetaNS.General.BackgroundColor].get_value()
            if bg:
                return QColor(bg)
            else:
                return QColor("#FFFFFF")
        # Text alignment role = left and vertically centered
        elif role == Qt.TextAlignmentRole:
            return Qt.AlignLeft | Qt.AlignVCenter
        return QVariant()

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                return str(self._visible_data.columns[section])
            elif orientation == Qt.Vertical:
                return str(self._visible_data.index[section])
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
                    styles: Series):
        ''' Update the model with new data, metadata, and collapsable information.
            This will refresh the view automatically.
        '''
        self.beginResetModel()
        self._visible_data = data
        self._styles = styles
        self.endResetModel()





class RenderedLogsTable(QTableView):
    def __init__(self, data:DataFrame=None, style:Series=None):
        super().__init__()
        self.data = data if data is not None else DataFrame()
        self.style = style if style is not None else Series()
        self.setSortingEnabled(False)
        self.setHorizontalScrollMode(QAbstractItemView.ScrollPerPixel)
        self.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.setSelectionMode(QAbstractItemView.SingleSelection)
        self.horizontalHeader().setStretchLastSection(True)

    def refresh(self, data:DataFrame=None, style:Series=None):
        self.setUpdatesEnabled(False)
        self.data = data if data is not None else self.data
        self.style = style if style is not None else self.style
        self.show_model()
        self.resizeColumnsToContents()
        # Last column does not expand indefinitely; horizontal scrolling enabled
        self.setHorizontalScrollMode(QAbstractItemView.ScrollPerPixel)
        self.horizontalHeader().setStretchLastSection(True)
        self.setUpdatesEnabled(True)
        return self
    
    def show_model(self):
        if self.data is not None:
            self.setModel(
                LogsTableModel(
                    self.data,
                    self.style
                )
            )
    
    def get_selected_rows(self) -> list[int]|None:
        selected_indexes = self.selectionModel().selectedRows() if self.selectionModel() else None
        if not selected_indexes or len(selected_indexes) == 0:
            return None
        return [index.row() for index in selected_indexes]

    def get_search_indexes(self, search_text: str, show_collapsed: bool=True) -> list[int]:
        mask = self.data.astype(str).apply(lambda x: x.str.contains(search_text, case=False, na=False)).any(axis=1)
        indexes = self.data.index[mask]
        iloc_indexes = [self.data.index.get_loc(idx) for idx in indexes]
        return iloc_indexes
