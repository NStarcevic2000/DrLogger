from PyQt5.QtWidgets import QDialog, QTreeWidget, QVBoxLayout, QHBoxLayout
from util.config_store import ConfigManager as CfgMan

class ReorderFilesPrompt(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Reorder Log Files")
        self.setModal(True)

        vbox = QVBoxLayout()
        hbox = QHBoxLayout()

        self.files_hierarchy_tree_view = QTreeWidget()
        hbox.addWidget(self.files_hierarchy_tree_view)

        vbox.addLayout(hbox)
        self.setLayout(vbox)

    def update():
        files = CfgMan().get(CfgMan().r.open_logs)