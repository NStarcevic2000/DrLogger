from PyQt5.QtWidgets import QHBoxLayout, QVBoxLayout, QLabel, QLineEdit, QFrame, QTableWidget, QTableWidgetItem, QComboBox
from PyQt5.QtWidgets import QComboBox, QCheckBox, QColorDialog, QTableWidgetItem
from PyQt5.QtGui import QColor

from PyQt5.QtCore import Qt, QModelIndex

from util.configStore import ConfigStore
from gui.editor.elements.presetSelector import PresetSelector
from PyQt5.QtWidgets import QColorDialog

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
        self.preset_selector = PresetSelector(self.cs, self.cs.r.color_logs.name)
        self.preset_selector.container.setAlignment(Qt.AlignRight)
        self.preset_selector.bind_cb(self.update_content)
        hbox = QHBoxLayout()
        hbox.addWidget(self.label)
        hbox.addLayout(self.preset_selector.container)
        self.addLayout(hbox)

        hbox = QHBoxLayout()

        self.color_pattern_editor = QTableWidget()
        self.color_pattern_editor.setColumnCount(4)
        self.color_pattern_editor.setHorizontalHeaderLabels(["Column", "Pattern", "Foreground", "Background"])
        self.color_pattern_editor.setRowCount(10)
        self.color_pattern_editor.setEditTriggers(QTableWidget.DoubleClicked)
        self.color_pattern_editor.setSelectionMode(QTableWidget.NoSelection)
        self.color_pattern_editor.verticalHeader().setDefaultSectionSize(20)
        self.color_pattern_editor.setColumnWidth(0, 100)
        self.color_pattern_editor.setColumnWidth(1, 100)
        self.color_pattern_editor.setColumnWidth(2, 90)
        self.color_pattern_editor.setColumnWidth(3, 90)
        for row in range(self.color_pattern_editor.rowCount()):
            for col in [2, 3]:
                item = self.color_pattern_editor.item(row, col)
                if not item:
                    item = QTableWidgetItem()
                    self.color_pattern_editor.setItem(row, col, item)
                # Make Foreground and Background cells not editable
                item.setFlags(item.flags() & ~Qt.ItemIsEditable)
        self.color_pattern_editor.setSizeAdjustPolicy(QTableWidget.AdjustToContents)
        self.color_pattern_editor.setMinimumWidth(
            sum([self.color_pattern_editor.columnWidth(i) for i in range(self.color_pattern_editor.columnCount())]) + 60
        )
        self.color_pattern_editor.cellClicked.connect(self.handle_cell_clicked)

        hbox.addWidget(self.color_pattern_editor)

        hbox1 = QHBoxLayout()
        self.choose_preset_label = QLabel("Enable Coloring:")
        self.choose_preset_combobox = QCheckBox()
        self.choose_preset_combobox.setToolTip("Enable or disable coloring")
        self.choose_preset_combobox.setChecked(
            self.cs.get(self.cs.r.color_logs.color_logs_enabled, True)
        )
        self.choose_preset_combobox.stateChanged.connect(
            lambda: self.cs.set(self.cs.r.color_logs.color_logs_enabled, self.choose_preset_combobox.isChecked())
        )
        self.choose_preset_combobox.setMaximumWidth(20)
        self.choose_preset_label.setMaximumWidth(self.choose_preset_label.fontMetrics().boundingRect("Enable Coloring:").width() + 5)
        hbox1.addWidget(self.choose_preset_label)
        hbox1.addWidget(self.choose_preset_combobox)
        hbox1.setAlignment(Qt.AlignTop)
        vbox = QVBoxLayout()
        vbox.addLayout(hbox1)
        vbox.setAlignment(Qt.AlignLeft)
        hbox.addLayout(vbox)

        self.addLayout(hbox)

        self.update_content()

        # Other connections
        self.color_pattern_editor.setSelectionBehavior(QTableWidget.SelectRows)
        self.color_pattern_editor.cellChanged.connect(self.save_color_config)

    def handle_cell_clicked(self, row, col):
        if col in [2, 3]:  # Foreground or Background columns
            self.open_color_picker(row, col)
            self.update_colors()
            self.save_color_config()

    def open_color_picker(self, row, col):
        if col in [2, 3]:  # Foreground or Background columns
            current_item = self.color_pattern_editor.item(row, col)
            color_dialog = QColorDialog(self.parent)
            color_dialog.setOption(QColorDialog.ShowAlphaChannel, False)
            color_dialog.setWindowModality(Qt.WindowModal)
            color_dialog.setWindowFlag(Qt.WindowStaysOnTopHint, True)
            color_dialog.raise_()
            color_dialog.activateWindow()
            if color_dialog.exec_():
                color = color_dialog.selectedColor()
                if color.isValid():
                    color_name = color.name()
                    if not current_item:
                        current_item = QTableWidgetItem(color_name)
                        self.color_pattern_editor.setItem(row, col, current_item)
                    else:
                        current_item.setText(color_name)

    def update_colors(self):
        for i in range(self.color_pattern_editor.rowCount()):
            # Set the colors of rows in this section
            fg_color = "#000000"  # default foreground: black
            bg_color = "#ffffff"  # default background: white
            if self.color_pattern_editor.item(i, 2):
                fg = self.color_pattern_editor.item(i, 2).text()
                if fg:
                    fg_color = fg
            if self.color_pattern_editor.item(i, 3):
                bg = self.color_pattern_editor.item(i, 3).text()
                if bg:
                    bg_color = bg
            for j in range(self.color_pattern_editor.columnCount()):
                item = self.color_pattern_editor.item(i, j)
                if item:
                    item.setForeground(QColor(fg_color))
                    item.setBackground(QColor(bg_color))

    def update_content(self):
        self.color_pattern_editor.blockSignals(True)
        self.choose_preset_combobox.blockSignals(True)
        color_patterns = self.cs.get(self.cs.r.color_logs.color_scheme, [])
        for i, (column, pattern, foreground, background) in enumerate(color_patterns):
            if i < self.color_pattern_editor.rowCount():
                self.color_pattern_editor.setItem(i, 0, QTableWidgetItem(column))
                self.color_pattern_editor.setItem(i, 1, QTableWidgetItem(pattern))
                self.color_pattern_editor.setItem(i, 2, QTableWidgetItem(foreground))
                self.color_pattern_editor.setItem(i, 3, QTableWidgetItem(background))
            else:
                break
        self.choose_preset_combobox.setChecked(
            self.cs.get(self.cs.r.color_logs.color_logs_enabled, True)
        )
        self.preset_selector.update_content()
        self.update_colors()
        self.color_pattern_editor.blockSignals(False)
        self.choose_preset_combobox.blockSignals(False)

    def save_color_config(self):
        # Save color scheme
        color_scheme = []
        for r in range(self.color_pattern_editor.rowCount()):
            items = [self.color_pattern_editor.item(r, c) for c in range(4)]
            if all(items) and all(item.text() for item in items):
                color_scheme.append(tuple(item.text() for item in items))
        self.cs.set(self.cs.r.color_logs.color_scheme, color_scheme)
        self.preset_selector.update_content()

    def setState(self, enabled=True):
        self.label.setEnabled(enabled)
        self.choose_preset_label.setEnabled(enabled)
        self.choose_preset_combobox.setEnabled(enabled)
