from PyQt5.QtWidgets import QTableWidget, QTableWidgetItem, QColorDialog
from PyQt5.QtGui import QColor
from PyQt5.QtCore import Qt

from enum import Enum

from util.config_store import ConfigManager as CfgMan
from gui.common.config_entry_intf import IConfigEntry

class TABLE_EDIT_TYPE(Enum):
    TEXT_EDIT = 0
    COLOR_PICKER = 1

class TableConfigEntry(IConfigEntry):
    def __init__(self,
                 parent,
                 config_name: str,
                 column_headers: list[str],
                 edit_types: list[TABLE_EDIT_TYPE],
                 column_width:int|None=None):
        self.parent = parent
        
        self.config_name = config_name
        self.edit_types = edit_types

        # ----- Layout -----
        self.table = QTableWidget()
        self.table.setColumnCount(len(column_headers))
        self.table.setHorizontalHeaderLabels(column_headers)
        self.table.setEditTriggers(QTableWidget.DoubleClicked)
        self.table.setSelectionMode(QTableWidget.NoSelection)
        self.table.verticalHeader().setDefaultSectionSize(20)
        self.table.setSizeAdjustPolicy(QTableWidget.AdjustToContents)
        self.table.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.table.horizontalHeader().setStretchLastSection(True)
        if column_width is not None:
            for col in range(self.table.columnCount()):
                self.table.setColumnWidth(col, column_width)
            self.table.setMinimumWidth(column_width * self.table.columnCount()+40)
            self.table.setMaximumWidth(column_width * self.table.columnCount()+40)
        # ----- Connections -----
        self.table.cellClicked.connect(self.handle_cell_clicked)
        self.table.cellChanged.connect(self.on_config_updated)

        self.update_content()
    

    def update_content(self):
        self.table.blockSignals(True)
        config_items = CfgMan().get(self.config_name, [])
        # Check the given data is a list of lists
        if not all(isinstance(item, list) for item in config_items):
            print(f"Invalid config data format: {config_items}")
            self.table.setRowCount(0)
            self.table.setColumnCount(0)
            self.table.blockSignals(False)
            return
        self.table.setRowCount(len(config_items) + 1)
        self.table.clearContents()
        for row, item in enumerate(config_items):
            for col in range(self.table.columnCount()):
                value = item[col] if col < len(item) else ""
                table_item = QTableWidgetItem(value)
                if col < len(self.edit_types) and self.edit_types[col] == TABLE_EDIT_TYPE.COLOR_PICKER:
                    # Make Foreground and Background cells not editable
                    table_item.setFlags(table_item.flags() & ~Qt.ItemIsEditable)
                self.table.setItem(row, col, table_item)
        self.table.blockSignals(False)
    
    def handle_cell_clicked(self, row, col):
        if self.edit_types[col] == TABLE_EDIT_TYPE.TEXT_EDIT:
            return  # No special handling for text edit
        elif col < len(self.edit_types) and self.edit_types[col] == TABLE_EDIT_TYPE.COLOR_PICKER:
            color_dialog = QColorDialog(self.table)
            color_dialog.setOption(QColorDialog.ShowAlphaChannel, False)
            color_dialog.setWindowModality(Qt.WindowModal)
            color_dialog.setWindowFlag(Qt.WindowStaysOnTopHint, True)
            color_dialog.raise_()
            color_dialog.activateWindow()
            if color_dialog.exec_():
                color = color_dialog.selectedColor()
                if color.isValid():
                    item = self.table.item(row, col)
                    if not item:
                        item = QTableWidgetItem()
                        # We will keep this unblocked because this is a user action
                        # and we want to capture it in on_config_updated
                        self.table.setItem(row, col, item)
                    item.setText(color.name())
    
    def on_config_updated(self):
        data = [
            [self.table.item(row, col).text() if self.table.item(row, col) else "" 
             for col in range(self.table.columnCount())]
            for row in range(self.table.rowCount())
        ]
        # Remove empty rows
        data = [row for row in data if any(cell for cell in row)]
        CfgMan().set(self.config_name, data)
        if self.parent and hasattr(self.parent, 'update_content'):
            self.parent.update_content()