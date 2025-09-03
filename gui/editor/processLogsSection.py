from PyQt5.QtWidgets import QHBoxLayout, QVBoxLayout, QLabel, QPushButton, QCheckBox, QLineEdit, QComboBox, QFrame

from PyQt5.QtCore import Qt

from util.configStore import ConfigStore
from gui.editor.elements.presetSelector import PresetSelector

class ProcessLogsSection(QVBoxLayout):
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

        self.label = QLabel("Process Logs:")

        self.preset_selector = PresetSelector(self.cs, self.cs.r.process_logs.name)
        self.preset_selector.container.setAlignment(Qt.AlignRight)
        self.preset_selector.bind_cb(self.update_content)
        hbox = QHBoxLayout()
        hbox.addWidget(self.label)
        hbox.addLayout(self.preset_selector.container)
        self.addLayout(hbox)

        self.input_pattern_editor_label = QLabel("Input Pattern:")
        self.input_pattern_editor = QLineEdit()
        self.input_pattern_editor.setPlaceholderText("Enter pattern for processing logs")
        self.input_pattern_editor.setAlignment(Qt.AlignLeft)
        self.input_pattern_editor.textChanged.connect(self.on_config_changed)

        hbox = QHBoxLayout()
        hbox.addWidget(self.input_pattern_editor_label)
        hbox.addWidget(self.input_pattern_editor)
        hbox.setAlignment(Qt.AlignLeft)
        self.addLayout(hbox)

        self.timestamp_format_editor_label = QLabel("Timestamp Format:")
        self.timestamp_format_editor = QLineEdit()
        self.timestamp_format_editor.setPlaceholderText("Enter pattern timestamp format")
        self.timestamp_format_editor.setAlignment(Qt.AlignLeft)
        self.timestamp_format_editor.textChanged.connect(self.on_config_changed)

        hbox = QHBoxLayout()
        hbox.addWidget(self.timestamp_format_editor_label)
        hbox.addWidget(self.timestamp_format_editor)
        hbox.setAlignment(Qt.AlignLeft)
        self.addLayout(hbox)

        self.setAlignment(Qt.AlignTop)

        self.update_content()

    def setState(self, enabled=True):
        self.label.setEnabled(enabled)
        self.choose_preset_label.setEnabled(enabled)
        self.choose_preset_combobox.setEnabled(enabled)

    def update_content(self):
        # Block signals to prevent on_config_changed from firing during programmatic updates
        self.input_pattern_editor.blockSignals(True)
        self.timestamp_format_editor.blockSignals(True)
        self.input_pattern_editor.setText(
            self.cs.get(self.cs.r.process_logs.input_pattern, "")
        )
        self.timestamp_format_editor.setText(
            self.cs.get(self.cs.r.process_logs.timestamp_format, "")
        )
        self.input_pattern_editor.blockSignals(False)
        self.timestamp_format_editor.blockSignals(False)
        self.preset_selector.update_content()

    def on_config_changed(self):
        self.cs.set(
            self.cs.r.process_logs.input_pattern, self.input_pattern_editor.text()
        )
        self.cs.set(
            self.cs.r.process_logs.timestamp_format, self.timestamp_format_editor.text()
        )
        self.preset_selector.update_content()