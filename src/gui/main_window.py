from PyQt5.QtWidgets import (
    QMainWindow, QToolBar, QAction, QShortcut, QFileDialog, QMenu, QToolButton
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QKeySequence

from logs_managing.logs_manager import LogsManager
from processor.processor_manager import ProcessorManager
from util.config_store import ConfigManager as CfgMan

from gui.save_logs_prompt import SaveLogsPrompt
from gui.editor.editor_prompt import EditorPrompt
from gui.common.status_bar import StatusBar
from gui.preset_prompt import PresetPrompt
from gui.common.rendered_logs_table import RenderedLogsTable
from gui.main_toolbar import MainToolbar

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


        self.footer_notebook = FooterNotebook()
        self.addDockWidget(Qt.BottomDockWidgetArea, self.footer_notebook)

        self.main_table = RenderedLogsTable(selectable=True)
        self.main_table.doubleClicked.connect(self.handle_row_double_click)

        self.save_logs_prompt = SaveLogsPrompt()

        self.toolbar = MainToolbar({
            "File": {
                "Open Logs...": self.open_logs_cmd,
                "Save All Logs... (Ctrl+S)": self.save_logs_cmd,
                "Save Selected Logs...": self.save_selected_logs_cmd,
                "Copy Selected Logs to Clipboard (Ctrl+C)": self.copy_selected_to_clipboard,
            },
            "Editor": self.editor_prompt.show_updated,
            "Presets": self.presets_prompt.show_updated,
        }, self)
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

        QShortcut(QKeySequence("Ctrl+C"), self, self.copy_selected_to_clipboard)
        QShortcut(QKeySequence("Ctrl+S"), self, self.save_logs_cmd)

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
    
    def update_table(self):
        data = LogsManager().get_data(show_collapsed=True)
        style = LogsManager().get_style(show_collapsed=True)
        self.main_table.refresh(data,style)

    def update(self):
        self.status_bar.call_in_background(ProcessorManager().run, self.update_table)

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

    def open_logs_cmd(self):
        options = QFileDialog.Options()
        options |= QFileDialog.ReadOnly
        files, _ = QFileDialog.getOpenFileNames(self, "Select Log Files", "", "All Files (*)", options=options)
        if files:
            CfgMan().set(CfgMan().r.open_logs.log_files, files)
        self.update()
    
    def save_logs_cmd(self):
        SaveLogsPrompt().save_to_file(
            LogsManager().get_data()
        )

    def save_selected_logs_cmd(self):
        SaveLogsPrompt().save_to_file(
            LogsManager().get_data(rows=self.main_table.get_selected_rows()[1])
        )
    
    def copy_selected_to_clipboard(self):
        SaveLogsPrompt().save_to_clipboard(
            LogsManager().get_data(rows=self.main_table.get_selected_rows()[1])
        )
