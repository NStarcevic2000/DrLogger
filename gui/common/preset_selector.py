from PyQt5.QtWidgets import QComboBox, QHBoxLayout, QLabel, QPushButton
import json

from util.configStore import ConfigStore
from enum import Enum

from gui.common.config_entry_intf import IConfigEntry

class PRESET_OPTION(Enum):
    MODIFY = "Modify"
    ADD = "Add"

class PresetSelector(IConfigEntry):
    def __init__(self,
                 parent,
                 configStore: ConfigStore,
                 configStoreNode: str):
        self.parent = parent
        self.cs: ConfigStore = configStore.get(configStoreNode)
        self.cached_presets:list = []
        self.cached_current_preset: str = ""

        self.container = QHBoxLayout()

        self.label = QLabel("Choose Preset:")
        self.container.addWidget(self.label)

        self.element = QComboBox()
        self.element.setEditable(True)
        self.element.setFixedSize(self.element.sizeHint())
        self.element.currentIndexChanged.connect(self.on_preset_selected)
        self.element.activated.connect(self.on_preset_selected)
        self.element.currentTextChanged.connect(self.update_content)
        self.element.setMinimumWidth(150)
        self.container.addWidget(self.element)

        self.func_button = QPushButton()
        self.func_button.clicked.connect(self.on_func_button_clicked)
        self.container.addWidget(self.func_button)

        self.update_content()

    def update_content(self):
        print("Updating preset selector content...")
        # Preserve current text while updating dropdown items
        current_text = self.element.currentText()
        self.element.blockSignals(True)
        self.element.clear()
        self.element.addItems(self.cs.list_presets())
        self.element.setCurrentText(current_text)
        self.element.blockSignals(False)
        # Define button text by the current state of the preset
        if not self.element.currentText().strip():
            self.func_button.blockSignals(True)
            self.func_button.setText(PRESET_OPTION.ADD.value)
            self.func_button.setEnabled(False)
            self.func_button.blockSignals(False)
        elif self.element.currentText() in self.cs.list_presets():
            self.func_button.blockSignals(True)
            self.func_button.setText(PRESET_OPTION.MODIFY.value)
            self.func_button.blockSignals(False)
            if self.cs.get_serialized() != self.cs.get_serialized(self.cs.get_preset(self.element.currentText())):
                self.func_button.blockSignals(True)
                self.func_button.setEnabled(True)
                self.func_button.blockSignals(False)
            else:
                self.func_button.blockSignals(True)
                self.func_button.setEnabled(False)
                self.func_button.blockSignals(False)
        else:
            self.func_button.blockSignals(True)
            self.func_button.setText(PRESET_OPTION.ADD.value)
            self.func_button.setEnabled(True)
            self.func_button.blockSignals(False)

    def on_func_button_clicked(self):
        self.cs.save_preset(self.element.currentText())
        self.on_config_updated()

    def on_preset_selected(self):
        # Set selected preset
        self.cs.apply_preset(self.element.currentText())
        self.on_config_updated()
    
    def on_config_updated(self):
        if self.parent and hasattr(self.parent, 'update_content'):
            self.parent.update_content()