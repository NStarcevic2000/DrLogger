from PyQt5.QtWidgets import QComboBox, QHBoxLayout, QLabel, QPushButton

from util.configStore import ConfigStore
from enum import Enum

class PRESET_OPTION(Enum):
    MODIFY = "Modify"
    ADD = "Add"

class PresetSelector(QComboBox):
    def __init__(self, 
                 configStore: ConfigStore,
                 configStoreNode: str):
        super().__init__()
        self.cs: ConfigStore = configStore.get(configStoreNode)
        self.cb: callable = None
        self.cached_presets:list = []
        self.cached_current_preset: str = ""

        self.container = QHBoxLayout()

        self.label = QLabel("Choose Preset:")
        self.container.addWidget(self.label)

        self.setEditable(True)
        self.setFixedSize(self.sizeHint())
        self.currentIndexChanged.connect(self.on_preset_selected)
        self.activated.connect(self.on_preset_selected)
        self.currentTextChanged.connect(self.update_content)
        self.container.addWidget(self)

        self.func_button = QPushButton()
        self.func_button.clicked.connect(self.on_func_button_clicked)
        self.container.addWidget(self.func_button)

        self.update_content()

    def bind_cb(self, cb: callable):
        self.cb = cb

    def update_content(self):
        # Preserve current text while updating dropdown items
        current_text = self.currentText()
        self.blockSignals(True)
        self.clear()
        self.addItems(self.cs.list_presets())
        self.setEditText(current_text)
        self.blockSignals(False)
        # Define button text by the current state of the preset
        if not self.currentText().strip():
            self.func_button.setText(PRESET_OPTION.ADD.value)
            self.func_button.setEnabled(False)
        elif self.currentText() in self.cs.list_presets():
            self.func_button.setText(PRESET_OPTION.MODIFY.value)
            if self.cs.get_serialized() != self.cs.get_preset(self.currentText()):
                self.func_button.setEnabled(True)
            else:
                self.func_button.setEnabled(False)
        else:
            self.func_button.setText(PRESET_OPTION.ADD.value)
            self.func_button.setEnabled(True)

    def on_func_button_clicked(self):
        self.cs.save_preset(self.currentText())
        if self.cb:
            self.cb()

    def on_preset_selected(self):
        # Set selected preset
        self.cs.apply_preset(self.currentText())
        if self.cb:
            self.cb()
