from PyQt5.QtWidgets import (
    QMainWindow, QToolBar, QAction, QShortcut
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QKeySequence

from processor.processor_manager import ProcessorManager

from gui.editor.editor_prompt import EditorPrompt
from gui.common.status_bar import StatusBar
from gui.preset_prompt import PresetPrompt
from gui.rendered_logs_table import RenderedLogsTable

from gui.find_toolbar import FindToolbar
from gui.footer_notebook import FooterNotebook, FOOTER_PAGE
from gui.meatadata_content import MetadataContent

class DrLoggerMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("DrLogger - All-in-one Log Viewer")
        self.setGeometry(200, 200, 1500, 700)
        
        self.font_size = 10  # Default font size

        self.editor_prompt = EditorPrompt(self.update)
        self.editor_prompt.setWindowModality(Qt.ApplicationModal)
        self.editor_prompt.setWindowFlag(Qt.WindowStaysOnTopHint, False)
        # self.editor_prompt.show_updated()

        self.presets_prompt = PresetPrompt()
        self.presets_prompt.setWindowModality(Qt.ApplicationModal)
        self.presets_prompt.setWindowFlag(Qt.WindowStaysOnTopHint, False)

        toolbar_cb = {
            "Editor": self.editor_prompt.show_updated,
            "Presets": self.presets_prompt.show_updated,
        }

        self.footer_notebook = FooterNotebook()
        self.addDockWidget(Qt.BottomDockWidgetArea, self.footer_notebook)

        self.main_table = RenderedLogsTable()
        self.main_table.doubleClicked.connect(self.handle_row_double_click)

        self.toolbar = QToolBar("Main Toolbar")
        for action_name, callback in toolbar_cb.items():
            action = QAction(action_name, self)
            action.triggered.connect(callback)
            self.toolbar.addAction(action)
        self.addToolBar(Qt.TopToolBarArea, self.toolbar)
        self.toolbar.setMovable(False)

        self.find_toolbar = FindToolbar(self, self.main_table)
        QShortcut(QKeySequence("Ctrl+F"), self, self.find_toolbar.toggle_visibility)
        self.addToolBarBreak(Qt.TopToolBarArea)
        self.addToolBar(Qt.TopToolBarArea, self.find_toolbar)

        self.setCentralWidget(self.main_table)
        self.set_table_font(self.font_size)

        QShortcut(QKeySequence("Ctrl++"), self, self.increase_font_size)
        QShortcut(QKeySequence("Ctrl+-"), self, self.decrease_font_size)

        QShortcut(QKeySequence(Qt.Key_Return), self, self.find_toolbar.find_next)

        self.keyboard_shortcuts_stack = {}

        self.status_bar = StatusBar()
        self.setStatusBar(self.status_bar)

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
        self.status_bar.call_in_background(ProcessorManager().run, on_done=self.main_table.refresh)

    def set_QShortcut_action(self, button: str, action: callable):
        shortcut = QShortcut(QKeySequence(button), self)
        shortcut.activated.connect(action)
        self.keyboard_shortcuts_stack[button] = shortcut

    def remove_QShortcut_action(self, button: str):
        if button in self.keyboard_shortcuts_stack:
            shortcut = self.keyboard_shortcuts_stack.pop(button)
            shortcut.activated.disconnect()
            shortcut.setParent(None)
            del shortcut
    
    def handle_row_double_click(self, index):
        MetadataContent().show_in_footer(index.row())
