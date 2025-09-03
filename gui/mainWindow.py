from PyQt5.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QTableWidget, QTableWidgetItem,
    QPushButton, QWidget, QMainWindow, QToolBar, QAction, QMessageBox, QShortcut
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QKeySequence

from pandas import DataFrame

from util.configStore import ConfigStore
from processor.processPipeline import ProcessPipeline

from processor.colorLogsProc import ColorLogsUtils

from gui.editor.editorPrompt import EditorPrompt
from gui.presetPrompt import PresetPrompt

class DrLogMainWindow(QMainWindow):
    def __init__(self, configStore: ConfigStore, processPipeline: ProcessPipeline):
        super().__init__()
        self.cs = configStore
        self.processPipeline = processPipeline
        self.clu = ColorLogsUtils(configStore)

        self.setWindowTitle("DrLog - All-in-one Log Viewer")
        self.setGeometry(200, 200, 1500, 700)
        
        self.font_size = 10  # Default font size

        self.editor_prompt = EditorPrompt(self.cs, self.processPipeline, self.update)
        self.editor_prompt.setWindowModality(Qt.ApplicationModal)
        self.editor_prompt.setWindowFlag(Qt.WindowStaysOnTopHint, False)
        self.editor_prompt.show()

        self.presets_prompt = PresetPrompt(self.cs)
        self.presets_prompt.setWindowModality(Qt.ApplicationModal)
        self.presets_prompt.setWindowFlag(Qt.WindowStaysOnTopHint, False)

        toolbar_cb = {
            "Editor": self.editor_prompt.show_updated,
            "Presets": self.presets_prompt.show_updated,
        }

        self.toolbar = QToolBar("Main Toolbar")
        for action_name, callback in toolbar_cb.items():
            action = QAction(action_name, self)
            action.triggered.connect(callback)
            self.toolbar.addAction(action)
        self.addToolBar(Qt.TopToolBarArea, self.toolbar)
        self.toolbar.setMovable(False)

        self.main_table = QTableWidget()
        self.main_table.setColumnCount(1)
        self.main_table.setHorizontalHeaderLabels(["Logs"])
        self.main_table.setRowCount(0)
        header = self.main_table.horizontalHeader()
        header.setSectionResizeMode(0, header.ResizeToContents)
        header.setStretchLastSection(True)

        self.setCentralWidget(self.main_table)
        self.set_table_font(self.font_size)

        QShortcut(QKeySequence("Ctrl++"), self, self.increase_font_size)
        QShortcut(QKeySequence("Ctrl+-"), self, self.decrease_font_size)

    def set_table_font(self, size):
        font = QFont()
        font.setPointSize(size)
        self.main_table.setFont(font)
        self.main_table.horizontalHeader().setFont(font)
        self.main_table.verticalHeader().setFont(font)

    def increase_font_size(self):
        self.font_size = min(self.font_size + 1, 32)
        self.set_table_font(self.font_size)
        self.main_table.verticalHeader().setDefaultSectionSize(self.font_size * 2)

    def decrease_font_size(self):
        self.font_size = max(self.font_size - 1, 6)
        self.set_table_font(self.font_size)
        self.main_table.verticalHeader().setDefaultSectionSize(self.font_size * 2)

    def update(self):
        self.processPipeline.run()
        data = self.processPipeline.get_data()
        if hasattr(data, "columns") and hasattr(data, "values") and isinstance(data, DataFrame) and not data.empty:
            self.main_table.setRowCount(0)
            self.main_table.setColumnCount(0)
            self.main_table.setColumnCount(len(data.columns))
            self.main_table.setHorizontalHeaderLabels([str(col) for col in data.columns])
            self.main_table.setRowCount(len(data))
            for row_idx, row in enumerate(data.values):
                for col_idx, value in enumerate(row):
                    self.main_table.setItem(row_idx, col_idx, QTableWidgetItem(str(value)))
            header = self.main_table.horizontalHeader()
            for col in range(len(data.columns) - 1):
                header.setSectionResizeMode(col, header.ResizeToContents)
            header.setSectionResizeMode(len(data.columns) - 1, header.Stretch)
        else:
            print("Data is not a pandas DataFrame.")
        self.clu.update_colors(self.main_table, self.processPipeline.get_color_metadata())
