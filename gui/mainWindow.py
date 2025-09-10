from PyQt5.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QTableWidget, QTableWidgetItem,
    QPushButton, QWidget, QMainWindow, QToolBar, QAction, QMessageBox, QShortcut
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QKeySequence, QColor

from pandas import DataFrame

from util.config_store import ConfigManager as CfgMan
from processor.processor_manager import ProcessorManager
from util.logs_manager import LogsManager

from gui.editor.editorPrompt import EditorPrompt
from gui.presetPrompt import PresetPrompt
from gui.rendered_logs_table import RenderedLogsTable

class DrLogMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("DrLog - All-in-one Log Viewer")
        self.setGeometry(200, 200, 1500, 700)
        
        self.font_size = 10  # Default font size

        self.editor_prompt = EditorPrompt(self.update)
        self.editor_prompt.setWindowModality(Qt.ApplicationModal)
        self.editor_prompt.setWindowFlag(Qt.WindowStaysOnTopHint, False)
        self.editor_prompt.show_updated()

        self.presets_prompt = PresetPrompt()
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

        self.main_table = RenderedLogsTable()

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
        self.main_table.refresh()
