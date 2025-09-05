from PyQt5.QtWidgets import QLineEdit, QHBoxLayout, QLabel
from PyQt5.QtGui import QIntValidator

from util.config_store import ConfigManager as CfgMan
from gui.common.config.config_entry_intf import IConfigEntry

class StringConfigEntry(IConfigEntry):
    def __init__(self,
                 parent,
                 descriptor_text: str,
                 config_name: str,
                 assert_type:type|None=None):
        self.parent = parent
        self.config_name = config_name
        self.assert_type = assert_type

        # ----- Layout -----
        self.container = QHBoxLayout()

        self.label = QLabel(descriptor_text)
        self.container.addWidget(self.label)

        self.element = QLineEdit()
        self.container.addWidget(self.element)
        # ----- Connections -----
        self.element.textChanged.connect(self.on_config_updated)
        if self.assert_type == int:
            self.element.setValidator(QIntValidator())
            self.element.setPlaceholderText("Enter an integer")

        self.update_content()

    def update_content(self):
        self.element.blockSignals(True)
        ret = CfgMan().get(self.config_name, "" if self.assert_type != int else 0)
        self.element.setText(str(ret) if self.assert_type == int else ret)
        self.element.blockSignals(False)

    def on_config_updated(self):
        text = self.element.text()
        if self.assert_type == int:
            try:
                value = int(text)
            except ValueError:
                value = 0
            CfgMan().set(self.config_name, value)
        else:
            CfgMan().set(self.config_name, text)
        if self.parent and hasattr(self.parent, 'update_content'):
            self.parent.update_content()
