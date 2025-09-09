from PyQt5.QtWidgets import QHBoxLayout, QVBoxLayout, QLabel, QLineEdit, QFrame, QTableWidget, QTableWidgetItem, QComboBox
from PyQt5.QtWidgets import QComboBox, QCheckBox

from PyQt5.QtCore import Qt

from util.config_store import ConfigManager as CfgMan
from util.config_enums import CONTEXTUALIZE_LINES_ENUM

from gui.common.preset_selector import PresetSelector
from gui.common.table_config_entry import TableConfigEntry, TABLE_EDIT_TYPE
from gui.common.bool_config_entry import BoolConfigEntry
from gui.common.string_config_entry import StringConfigEntry
from gui.common.enum_config_entry import EnumConfigEntry

class FilterLogsSection(QVBoxLayout):
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

        self.label = QLabel("Filter Logs:")

        self.preset_selector = PresetSelector(self, CfgMan().r.filter_logs.name)
        self.preset_selector.container.setAlignment(Qt.AlignRight)
        
        hbox = QHBoxLayout()
        hbox.addWidget(self.label)
        hbox.addLayout(self.preset_selector.container)
        self.addLayout(hbox)

        hbox = QHBoxLayout()
        self.filter_pattern_editor = TableConfigEntry(
            self,
            
            CfgMan().r.filter_logs.filter_pattern,
            ["Column", "Pattern"],
            [TABLE_EDIT_TYPE.TEXT_EDIT, TABLE_EDIT_TYPE.TEXT_EDIT],
            column_width=150
        )
        hbox.addWidget(self.filter_pattern_editor.table)

        vbox = QVBoxLayout()
        vbox.setAlignment(Qt.AlignTop)
        self.keep_hidden_logs = BoolConfigEntry(
            self,
            
            "Keep Hidden Logs:",
            CfgMan().r.filter_logs.keep_hidden_logs
        )
        vbox.addLayout(self.keep_hidden_logs.container)
        self.contextualize_lines_count = StringConfigEntry(
            self,
            
            "Contextualize Spread:",
            CfgMan().r.filter_logs.contextualize_lines_count,
            assert_type=int
        )
        vbox.addLayout(self.contextualize_lines_count.container)
        self.contextualize_lines_type = EnumConfigEntry(
            self,
            
            "Contextualize Type:",
            CfgMan().r.filter_logs.contextualize_lines,
            CONTEXTUALIZE_LINES_ENUM.get_values()
        )
        vbox.addLayout(self.contextualize_lines_type.container)
        vbox.addStretch(1)

        hbox.addLayout(vbox)
        self.addLayout(hbox)

        self.update_content()

    def update_content(self):
        self.filter_pattern_editor.update_content()
        self.keep_hidden_logs.update_content()
        self.contextualize_lines_count.update_content()
        self.contextualize_lines_type.update_content()
        self.preset_selector.update_content()