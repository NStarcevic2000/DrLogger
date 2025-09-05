from PyQt5.QtWidgets import QCheckBox, QHBoxLayout, QLabel

from util.configStore import ConfigStore
from gui.common.config_entry_intf import IConfigEntry

class BoolConfigEntry(IConfigEntry):
    def __init__(self,
                 parent,
                 configStore: ConfigStore,
                 descriptor_text: str,
                 config_name: str):
        self.parent = parent
        self.cs = configStore
        self.config_name = config_name

        # ----- Layout -----
        self.container = QHBoxLayout()

        self.label = QLabel(descriptor_text)
        self.container.addWidget(self.label)

        self.element = QCheckBox()
        self.container.addWidget(self.element)
        # ----- Connections -----
        self.element.stateChanged.connect(self.on_config_updated)

        self.update_content()

    def update_content(self):
        self.element.blockSignals(True)
        self.element.setChecked(self.cs.get(self.config_name, False))
        self.element.blockSignals(False)

    def on_config_updated(self):
        self.cs.set(self.config_name, self.element.isChecked())
        if self.parent and hasattr(self.parent, 'update_content'):
            self.parent.update_content()