from PyQt5.QtWidgets import QHBoxLayout, QVBoxLayout, QLabel, QPushButton, QMessageBox, QTableWidget, QTableWidgetItem, QLineEdit, QFrame
from PyQt5.QtGui import QIntValidator, QColor
from PyQt5.QtCore import Qt

from pandas import DataFrame

from util.config_store import ConfigManager as CfgMan
from processor.processor_manager import ProcessorManager
from logs_managing.logs_manager import LogsManager

from gui.rendered_logs_table import RenderedLogsTable

class PreviewLogsSection(QVBoxLayout):
    def __init__(self, parent:None):
        super().__init__()
        self.parent = parent

        # Add separator
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Sunken)
        self.addWidget(separator)
        
        self.label = QLabel("Preview:")

        self.preview_button = QPushButton("Preview")
        self.preview_button.clicked.connect(self.preview_logs_cmd)
        self.preview_button.setFixedSize(self.preview_button.sizeHint())

        hbox = QHBoxLayout()
        hbox.addWidget(self.label)
        hbox.addWidget(self.preview_button)
        self.addLayout(hbox)
        
        self.preview_logs_table = RenderedLogsTable()

        vbox = QVBoxLayout()

        self.preview_lines_label = QLabel("Preview lines:")
        self.preview_lines_label.setAlignment(Qt.AlignRight)
        self.preview_lines_edit = QLineEdit()
        self.preview_lines_edit.setPlaceholderText("Enter number of lines to preview")
        self.preview_lines_edit.setFixedWidth(50)
        self.preview_lines_edit.setAlignment(Qt.AlignRight)
        # Limit to only set numbers
        self.preview_lines_edit.setValidator(QIntValidator(1, 1000, self.parent))
        self.preview_lines_edit.setText(
            str(CfgMan().get(CfgMan().r.preferences.preview_max_lines, 5))
        )  # Default to 5 lines
        self.preview_lines_edit.textChanged.connect(
            lambda text: CfgMan().set(CfgMan().r.preferences.preview_max_lines, int(text)) if text.isdigit() else None
        )
        
        hbox = QHBoxLayout()
        hbox.addWidget(self.preview_lines_label)
        hbox.addWidget(self.preview_lines_edit)
        hbox.setAlignment(Qt.AlignRight)
        vbox.addLayout(hbox)
        vbox.setAlignment(Qt.AlignTop)

        # Expand the table maximally
        self.preview_logs_table.horizontalHeader().setStretchLastSection(True)

        hbox = QHBoxLayout()
        hbox.addWidget(self.preview_logs_table, stretch=1)
        hbox.addLayout(vbox)
        self.addLayout(hbox)

        # Set this layout to the bottom of the parent layout
        self.setAlignment(Qt.AlignBottom)

    def setState(self, enabled=True):
        self.label.setEnabled(enabled)
    
    def preview_logs_cmd(self):
        def cmd():
            self.preview_logs_table.refresh(
                CfgMan().get(CfgMan().r.preferences.preview_max_lines, 5)
            )
        self.parent.status_bar.call(cmd)