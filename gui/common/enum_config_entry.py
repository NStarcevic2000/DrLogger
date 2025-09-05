from PyQt5.QtWidgets import QComboBox, QHBoxLayout, QLabel
from PyQt5.QtCore import Qt

from util.configStore import ConfigStore
from gui.common.config_entry_intf import IConfigEntry

class EnumConfigEntry(IConfigEntry):
    def __init__(self,
                 parent,
                 configStore: ConfigStore,
                 descriptor_text: str,
                 config_name: str,
                 enum_values:list[str]):
        self.parent = parent
        self.cs = configStore
        self.config_name = config_name
        self.possible_values = enum_values

        # ----- Layout -----
        self.wrapper = QHBoxLayout()
        self.wrapper.setContentsMargins(0, 0, 0, 0)
        self.wrapper.setSpacing(5)

        self.label = QLabel(descriptor_text)
        self.label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.wrapper.addWidget(self.label)

        self.element = QComboBox()
        self.element.addItems(self.possible_values)
        self.element.setEditable(False)
        self.element.setMinimumWidth(120)
        self.wrapper.addWidget(self.element)

        self.wrapper.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        # ----- Connections -----
        self.element.currentIndexChanged.connect(self.on_config_updated)

        self.update_content()
    
    def update_content(self):
        self.element.blockSignals(True)
        current_value = self.cs.get(self.config_name, self.possible_values[0])
        if current_value in self.possible_values:
            index = self.possible_values.index(current_value)
            self.element.setCurrentIndex(index)
        else:
            print(f"Warning: Current value '{current_value}' not in possible values {self.possible_values}. Setting to default.")
            self.element.setCurrentIndex(0)
            self.cs.set(self.config_name, self.possible_values[0])
        self.element.blockSignals(False)
    
    def on_config_updated(self):
        selected_value = self.element.currentText()
        self.cs.set(self.config_name, selected_value)
        if self.parent and hasattr(self.parent, 'update_content'):
            self.parent.update_content()