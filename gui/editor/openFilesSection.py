from PyQt5.QtWidgets import QHBoxLayout, QVBoxLayout, QLabel, QPushButton, QCheckBox, QLineEdit, QComboBox, QFrame, QFileDialog

from PyQt5.QtCore import Qt

from util.config_store import ConfigManager as CfgMan
from util.config_enums import KEEP_SOURCE_FILE_LOCATION_ENUM

from gui.common.enum_config_entry import EnumConfigEntry

class OpenFilesSection(QVBoxLayout):
    def __init__(self, parent,
                 pipeline=None,
                 call_update_cb=None):
        super().__init__()
        self.parent = parent
        self.pipeline = pipeline
        self.call_update_cb = call_update_cb

        self.label = QLabel()
        self.set_label()

        self.browse_button = QPushButton("Browse")
        self.browse_button.clicked.connect(self.open_logs_cmd)
        self.browse_button.setFixedSize(self.browse_button.sizeHint())

        hbox = QHBoxLayout()
        hbox.addWidget(self.label, alignment=Qt.AlignLeft)
        hbox.addWidget(self.browse_button, alignment=Qt.AlignRight)
        self.addLayout(hbox)

        self.keep_source_files_column_selector = EnumConfigEntry(
            self,
            "Keep Source Files as Column:",
            CfgMan().r.open_logs.keep_source_file_location,
            KEEP_SOURCE_FILE_LOCATION_ENUM.get_values()
        )

        self.setAlignment(Qt.AlignTop)

    def open_logs_cmd(self):
        # Open file dialog to select log files
        options = QFileDialog.Options()
        options |= QFileDialog.ReadOnly
        files, _ = QFileDialog.getOpenFileNames(self.parent, "Select Log Files", "", "All Files (*)", options=options)
        if files:
            CfgMan().set(CfgMan().r.open_logs.log_files, files)
        self.set_label()
        self.pipeline.run()
        self.call_update_cb()
    
    def set_label(self):
        files = CfgMan().get(CfgMan().r.open_logs.log_files, [])
        format = "Open Logs: <span style='color: gray;'>{}</span>"
        if files:
            if len(files) == 1:
                self.label.setText(format.format(files[0]))
            else:
                self.label.setText(format.format(f"{'/'.join(files[0].split('/')[:-1])+"/..."} [{len(files)} files opened]"))
        else:
            self.label.setText("Open Logs: No files opened")
    
    def update_content(self):
        self.keep_source_files_column_selector.update_content()
