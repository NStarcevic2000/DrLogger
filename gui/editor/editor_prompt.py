from gui.editor.open_logs_section import OpenFilesSection
from gui.editor.process_logs_section import ProcessLogsSection
from gui.editor.color_logs_section import ColorLogsSection
from gui.editor.filtar_logs_section import FilterLogsSection
from gui.editor.preview_logs_section import PreviewLogsSection

from PyQt5.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QMessageBox, QFrame
from PyQt5.QtCore import Qt

class EditorPrompt(QDialog):
    def __init__(self=None, on_run_cmd=None):
        super().__init__()
        self.setWindowTitle("Editor Prompt")
        self.setGeometry(100, 100, 800, 600)
        self.layout = QVBoxLayout(self)
        self.layout.setAlignment(Qt.AlignTop)

        self.on_run_cmd = on_run_cmd

        # A horizontal box with horizontally aligned updatable label,
        # A "Browse" button, and a "Save" button, stuck to the top
        self.open_files_section = OpenFilesSection(self, self.update)
        self.open_files_section.setAlignment(Qt.AlignTop)
        self.layout.addLayout(self.open_files_section)

        self.process_logs_section = ProcessLogsSection(self, self.update)
        self.process_logs_section.setAlignment(Qt.AlignTop)
        self.layout.addLayout(self.process_logs_section)

        hbox = QHBoxLayout()
        hbox.addStretch(1)

        self.color_logs_section = ColorLogsSection(self, self.update)
        self.color_logs_section.setAlignment(Qt.AlignTop)
        hbox.addLayout(self.color_logs_section)

        separator = QFrame()
        separator.setFrameShape(QFrame.VLine)
        separator.setFrameShadow(QFrame.Sunken)
        hbox.addWidget(separator)

        self.filter_logs_section = FilterLogsSection(self, self.update)
        self.filter_logs_section.setAlignment(Qt.AlignTop)
        hbox.addLayout(self.filter_logs_section)

        self.layout.addLayout(hbox)

        self.preview_logs_section = PreviewLogsSection(self)
        self.layout.addLayout(self.preview_logs_section)

        self.save_button = QPushButton("Run")
        self.save_button.clicked.connect(self.run_cmd)

        self.status_label = QLabel("Status: Ready")
        self.status_label.setAlignment(Qt.AlignLeft)
        
        hbox = QHBoxLayout()
        hbox.addWidget(self.status_label)
        hbox.addStretch(1)
        hbox.addWidget(self.save_button)
        self.layout.addLayout(hbox)

    def show_updated(self):
        self.update()
        self.show()

    def run_cmd(self):
        if self.on_run_cmd:
            self.on_run_cmd()
        self.close()

    def update(self):
        self.open_files_section.update_content()
        self.process_logs_section.update_content()
        self.color_logs_section.update_content()
        self.filter_logs_section.update_content()
        self.preview_logs_section.update()

    def set_status(self, message):
        self.status_label.setText(f"Status: {message}")