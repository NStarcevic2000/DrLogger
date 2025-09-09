from PyQt5.QtWidgets import QHBoxLayout, QVBoxLayout, QLabel, QFrame

from PyQt5.QtCore import Qt

from util.config_store import ConfigManager as CfgMan
from gui.common.preset_selector import PresetSelector

from gui.common.string_config_entry import StringConfigEntry

class ProcessLogsSection(QVBoxLayout):
    def __init__(self, parent, pipeline=None, call_update_cb=None):
        super().__init__()
        self.parent = parent
        self.pipeline = pipeline
        self.call_update_cb = call_update_cb

        # Add separator
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Sunken)
        self.addWidget(separator)

        self.label = QLabel("Process Logs:")

        self.preset_selector = PresetSelector(self, CfgMan().r.process_logs.name)
        self.preset_selector.container.setAlignment(Qt.AlignRight)
        hbox = QHBoxLayout()
        hbox.addWidget(self.label)
        hbox.addLayout(self.preset_selector.container)
        self.addLayout(hbox)

        self.input_pattern_entry = StringConfigEntry(
            self,
            "Input Pattern:",
            CfgMan().r.process_logs.input_pattern
        )
        self.addLayout(self.input_pattern_entry.container)

        self.timestamp_format_entry = StringConfigEntry(
            self,
            "Timestamp Format:",
            CfgMan().r.process_logs.timestamp_format
        )
        self.addLayout(self.timestamp_format_entry.container)

        self.setAlignment(Qt.AlignTop)
        self.update_content()

    def update_content(self):
        self.input_pattern_entry.update_content()
        self.timestamp_format_entry.update_content()
        self.preset_selector.update_content()