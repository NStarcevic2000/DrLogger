from PyQt5.QtWidgets import QHBoxLayout, QVBoxLayout, QLabel, QFrame
from PyQt5.QtGui import QColor

from PyQt5.QtCore import Qt

from util.configStore import ConfigStore
from gui.common.preset_selector import PresetSelector
from gui.common.table_config_entry import TableConfigEntry, TABLE_EDIT_TYPE
from gui.common.bool_config_entry import BoolConfigEntry

class ColorLogsSection(QVBoxLayout):
    def __init__(self, parent, configStore:ConfigStore, pipeline=None, call_update_cb=None):
        super().__init__()
        self.cs = configStore
        self.parent = parent
        self.pipeline = pipeline
        self.call_update_cb = call_update_cb

        # Add separator
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Sunken)
        self.addWidget(separator)

        self.label = QLabel("Color Logs:")
        self.preset_selector = PresetSelector(self, self.cs, self.cs.r.color_logs.name)
        self.preset_selector.container.setAlignment(Qt.AlignRight)
        
        hbox = QHBoxLayout()
        hbox.addWidget(self.label)
        hbox.addLayout(self.preset_selector.container)
        self.addLayout(hbox)

        hbox = QHBoxLayout()
        self.color_pattern_editor = TableConfigEntry(
            self,
            self.cs,
            self.cs.r.color_logs.color_scheme,
            ["Column", "Pattern", "Foreground", "Background"],
            [TABLE_EDIT_TYPE.TEXT_EDIT, TABLE_EDIT_TYPE.TEXT_EDIT, TABLE_EDIT_TYPE.COLOR_PICKER, TABLE_EDIT_TYPE.COLOR_PICKER],
            column_width=100
        )
        hbox.addWidget(self.color_pattern_editor.table)

        vbox = QVBoxLayout()
        vbox.setAlignment(Qt.AlignTop)
        self.enable_coloring = BoolConfigEntry(
            self,
            self.cs,
            "Enable Coloring:",
            self.cs.r.color_logs.color_logs_enabled
        )
        vbox.addLayout(self.enable_coloring.container)
        vbox.addStretch(1)

        hbox.addLayout(vbox)

        self.addLayout(hbox)

        self.update_content()

    def update_content(self):
        self.color_pattern_editor.update_content()
        self.update_colors()
        self.enable_coloring.update_content()
        self.preset_selector.update_content()
    
    def update_colors(self):
        self.color_pattern_editor.table.blockSignals(True)
        for i in range(self.color_pattern_editor.table.rowCount()):
            # Set the colors of rows in this section
            fg_color = "#000000"  # default foreground: black
            bg_color = "#ffffff"  # default background: white
            if self.color_pattern_editor.table.item(i, 2):
                fg = self.color_pattern_editor.table.item(i, 2).text()
                if fg:
                    fg_color = fg
            if self.color_pattern_editor.table.item(i, 3):
                bg = self.color_pattern_editor.table.item(i, 3).text()
                if bg:
                    bg_color = bg
            for j in range(self.color_pattern_editor.table.columnCount()):
                item = self.color_pattern_editor.table.item(i, j)
                if item:
                    item.setForeground(QColor(fg_color))
                    item.setBackground(QColor(bg_color))
        self.color_pattern_editor.table.blockSignals(False)
