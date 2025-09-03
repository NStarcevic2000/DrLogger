from PyQt5.QtWidgets import QHBoxLayout, QVBoxLayout, QLabel, QLineEdit, QFrame, QTableWidget, QTableWidgetItem, QComboBox
from PyQt5.QtWidgets import QComboBox, QCheckBox

from PyQt5.QtCore import Qt

from util.configStore import ConfigStore
from configStoreImpl import CONTEXTUALIZE_LINES_ENUM

from gui.editor.elements.presetSelector import PresetSelector

class FilterLogsSection(QVBoxLayout):
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

        self.label = QLabel("Filter Logs:")

        self.preset_selector = PresetSelector(self.cs, self.cs.r.filter_logs.name)
        self.preset_selector.container.setAlignment(Qt.AlignRight)
        self.preset_selector.bind_cb(self.update_content)
        hbox = QHBoxLayout()
        hbox.addWidget(self.label)
        hbox.addLayout(self.preset_selector.container)
        self.addLayout(hbox)

        hbox = QHBoxLayout()
        self.filter_pattern_editor = QTableWidget()
        self.filter_pattern_editor.setColumnCount(2)
        self.filter_pattern_editor.setHorizontalHeaderLabels(["Column", "Pattern"])
        self.filter_pattern_editor.setRowCount(10)
        self.filter_pattern_editor.setEditTriggers(QTableWidget.DoubleClicked | QTableWidget.SelectedClicked)
        self.filter_pattern_editor.verticalHeader().setDefaultSectionSize(20)
        self.filter_pattern_editor.setColumnWidth(0, 150)
        self.filter_pattern_editor.setSizeAdjustPolicy(QTableWidget.AdjustToContents)
        self.filter_pattern_editor.setMinimumWidth(
            self.filter_pattern_editor.columnWidth(0) + self.filter_pattern_editor.columnWidth(1) + 60
        )
        self.filter_pattern_editor.setSelectionMode(QTableWidget.NoSelection)
        self.filter_pattern_editor.setSelectionBehavior(QTableWidget.SelectRows)
        # Populate the table with existing patterns

        hbox.addWidget(self.filter_pattern_editor)

        vbox = QVBoxLayout()
        
        hbox1 = QHBoxLayout()
        self.keep_hidden_logs = QLabel("Contextualize Lines Type:")
        self.keep_hidden_logs_combobox = QCheckBox("Keep Hidden Logs:")
        self.keep_hidden_logs_combobox.setToolTip("Choose whether to keep hidden logs:")
        self.keep_hidden_logs_combobox.setChecked(
            self.cs.get(self.cs.r.filter_logs.keep_hidden_logs, True)
        )
        self.keep_hidden_logs_combobox.stateChanged.connect(
            lambda: self._set_and_update(
                lambda: self.cs.set(
                    self.cs.r.filter_logs.keep_hidden_logs,
                    self.keep_hidden_logs_combobox.isChecked()
                )
            )
        )
        hbox1.addWidget(self.keep_hidden_logs)
        hbox1.addWidget(self.keep_hidden_logs_combobox)
        vbox.addLayout(hbox1)

        hbox1 = QHBoxLayout()
        self.contextualize_lines_label = QLabel("Contextualize Filtered Lines:")
        self.contextualize_lines_editor = QLineEdit()
        self.contextualize_lines_editor.setPlaceholderText("Enter number of lines to contextualize")
        self.contextualize_lines_editor.setAlignment(Qt.AlignLeft)
        self.contextualize_lines_editor.textChanged.connect(
            lambda: self._set_and_update(
                lambda: self.cs.set(
                    self.cs.r.filter_logs.contextualize_lines_count,
                    int(self.contextualize_lines_editor.text()) if self.contextualize_lines_editor.text().isdigit() else 0
                )
            )
        )
        
        hbox1.addWidget(self.contextualize_lines_label)
        hbox1.addWidget(self.contextualize_lines_editor)
        vbox.setAlignment(Qt.AlignTop)
        vbox.addLayout(hbox1)

        hbox1 = QHBoxLayout()
        self.contextualize_lines_enum_label = QLabel("Contextualize Lines Type:")
        self.contextualize_lines_enum_combobox = QComboBox()
        self.contextualize_lines_enum_combobox.setToolTip("Choose contextualization type:")
        self.contextualize_lines_enum_combobox.addItems(
            CONTEXTUALIZE_LINES_ENUM.get_values()
        )
        self.contextualize_lines_enum_combobox.currentIndexChanged.connect(
            lambda: self._set_and_update(
                lambda: self.cs.set(
                    self.cs.r.filter_logs.contextualize_lines,
                    self.contextualize_lines_enum_combobox.currentText()
                )
            )
        )

        hbox1.addWidget(self.contextualize_lines_enum_label)
        hbox1.addWidget(self.contextualize_lines_enum_combobox)
        hbox1.setAlignment(Qt.AlignLeft)
        vbox.addLayout(hbox1)

        hbox.addLayout(vbox)

        self.addLayout(hbox)

        self.update_content()

    def _set_and_update(self, set_func):
        set_func()
        self.preset_selector.update_content()

    def update_content(self):
        self.filter_pattern_editor.blockSignals(True)
        self.contextualize_lines_editor.blockSignals(True)
        self.contextualize_lines_enum_combobox.blockSignals(True)
        self.contextualize_lines_enum_combobox.blockSignals(True)
        filter_patterns = self.cs.get(self.cs.r.filter_logs.filter_pattern, [])
        for i, (column, pattern) in enumerate(filter_patterns):
            if i < self.filter_pattern_editor.rowCount():
                self.filter_pattern_editor.setItem(i, 0, QTableWidgetItem(column))
                self.filter_pattern_editor.setItem(i, 1, QTableWidgetItem(pattern))
            else:
                break
        self.filter_pattern_editor.cellChanged.connect(
            lambda: self._set_and_update(
                lambda: self.cs.set(
                    self.cs.r.filter_logs.filter_pattern,
                    [
                        (self.filter_pattern_editor.item(row, 0).text() if self.filter_pattern_editor.item(row, 0) else "",
                         self.filter_pattern_editor.item(row, 1).text() if self.filter_pattern_editor.item(row, 1) else "")
                        for row in range(self.filter_pattern_editor.rowCount())
                        if self.filter_pattern_editor.item(row, 0) and self.filter_pattern_editor.item(row, 1)
                    ]
                )
            )
        )
        self.contextualize_lines_editor.setText(
            str(self.cs.get(self.cs.r.filter_logs.contextualize_lines_count, 0))
        )
        self.contextualize_lines_enum_combobox.setCurrentIndex(
            CONTEXTUALIZE_LINES_ENUM.get_values().index(
                self.cs.get(self.cs.r.filter_logs.contextualize_lines, CONTEXTUALIZE_LINES_ENUM.NONE.value)
            )
        )
        self.keep_hidden_logs_combobox.setChecked(
            self.cs.get(self.cs.r.filter_logs.keep_hidden_logs, True)
        )
        self.preset_selector.update_content()
        self.filter_pattern_editor.blockSignals(False)
        self.contextualize_lines_editor.blockSignals(False)
        self.contextualize_lines_enum_combobox.blockSignals(False)
        self.keep_hidden_logs_combobox.blockSignals(False)
