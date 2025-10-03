from PyQt5.QtWidgets import QDialog, QVBoxLayout, QPushButton, QLabel, QComboBox, QCheckBox, QHBoxLayout, QTextEdit, QLineEdit
from PyQt5.QtCore import Qt

from util.config_manager import ConfigManager as CfgMan
import json
from PyQt5.QtWidgets import QTableWidget, QTableWidgetItem
from PyQt5.QtWidgets import QTableWidgetItem

from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QComboBox,
    QCheckBox, QTextEdit, QLineEdit, QTreeWidget, QTreeWidgetItem, QFileDialog, QWidget, QSizePolicy
)

class PresetPrompt(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Preset Prompt")
        self.setGeometry(100, 100, 900, 600)
        self.pm_map:dict = {}

        self.update_pm_map()

        main_layout = QHBoxLayout(self)
        self.setLayout(main_layout)

        # Left side: Tree view and buttons
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setAlignment(Qt.AlignTop)

        self.preset_tree_view = QTreeWidget()
        self.preset_tree_view.setHeaderLabels(["", "Category", "Preset"])
        self.preset_tree_view.setColumnCount(3)
        self.preset_tree_view.setSelectionMode(QTreeWidget.SingleSelection)
        self.preset_tree_view.itemSelectionChanged.connect(self.on_tree_selection_changed)
        self.preset_tree_view.itemChanged.connect(self.on_item_changed)  # Called by checking of the checkbox
        self.preset_tree_view.setItemsExpandable(True)
        self.preset_tree_view.setAnimated(True)
        self.preset_tree_view.setRootIsDecorated(True)
        # Shrink columns to fit content and allow dynamic resizing
        header = self.preset_tree_view.header()
        header.setSectionResizeMode(0, header.ResizeToContents)
        header.setSectionResizeMode(1, header.ResizeToContents)
        header.setSectionResizeMode(2, header.ResizeToContents)
        left_layout.addWidget(self.preset_tree_view)

        btn_layout = QHBoxLayout()
        self.export_btn = QPushButton("Export")
        self.export_btn.clicked.connect(self.export_presets)
        self.import_btn = QPushButton("Import")
        self.import_btn.clicked.connect(self.import_presets)
        btn_layout.addWidget(self.export_btn)
        btn_layout.addWidget(self.import_btn)
        left_layout.addLayout(btn_layout)

        main_layout.addWidget(left_widget, 2)

        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setAlignment(Qt.AlignTop)

        self.checked_label = QLabel("Export Presets (JSON):")
        right_layout.addWidget(self.checked_label)
        self.checked_json_view = QTextEdit()
        self.checked_json_view.setReadOnly(True)
        right_layout.addWidget(self.checked_json_view)

        self.detail_label = QLabel("Edit Selected Preset:")
        right_layout.addWidget(self.detail_label)
        self.detail_table = QTableWidget()
        self.detail_table.setColumnCount(2)
        self.detail_table.setHorizontalHeaderLabels(["Key", "Value"])
        self.detail_table.horizontalHeader().setStretchLastSection(True)
        self.detail_table.setEditTriggers(QTableWidget.AllEditTriggers)
        self.detail_table.itemChanged.connect(self.on_table_item_changed)
        right_layout.addWidget(self.detail_table)

        main_layout.addWidget(right_widget, 3)

        # Anytime window is refreshed update content
        self.update_content()

    def show_updated(self):
        self.update_content()
        self.show()

    def update_content(self):
        self.update_pm_map()
        self.populate_tree()
        self.update_checked_json()

    
    def update_pm_map(self):
        self.pm_map = {
            CfgMan().r.process_logs.name: CfgMan().get(CfgMan().r.process_logs.name).get_all_presets(),
            CfgMan().r.color_logs.name: CfgMan().get(CfgMan().r.color_logs.name).get_all_presets(),
            CfgMan().r.filter_logs.name: CfgMan().get(CfgMan().r.filter_logs.name).get_all_presets(),
        }

    def populate_tree(self):
        self.preset_tree_view.clear()
        for category, preset_dict in self.pm_map.items():
            category_item = QTreeWidgetItem(["", category, ""])
            category_item.setFlags(category_item.flags() | Qt.ItemIsTristate | Qt.ItemIsUserCheckable | Qt.ItemIsEnabled)
            category_item.setCheckState(0, Qt.Unchecked)
            self.preset_tree_view.addTopLevelItem(category_item)
            if isinstance(preset_dict, dict):
                for preset_name, preset_data in preset_dict.items():
                    preset_item = QTreeWidgetItem(["", category, preset_name])
                    preset_item.setFlags(preset_item.flags() | Qt.ItemIsUserCheckable | Qt.ItemIsSelectable | Qt.ItemIsEnabled)
                    preset_item.setCheckState(0, Qt.Unchecked)
                    preset_item.setData(0, Qt.UserRole, preset_data)
                    category_item.addChild(preset_item)
            else:
                preset_item = QTreeWidgetItem(["", category, ""])
                preset_item.setFlags(preset_item.flags() | Qt.ItemIsUserCheckable | Qt.ItemIsSelectable | Qt.ItemIsEnabled)
                preset_item.setCheckState(0, Qt.Unchecked)
                preset_item.setData(0, Qt.UserRole, preset_dict)
                category_item.addChild(preset_item)

    def on_tree_selection_changed(self):
        selected = self.preset_tree_view.selectedItems()
        if selected:
            preset_item = selected[0]
            category = preset_item.text(1)
            preset_name = preset_item.text(2)
            # Pass category and preset_name to populate_detail_table for further use
            self.populate_detail_table(category, preset_name)
        else:
            self.detail_table.setRowCount(0)

    def on_item_changed(self, item, column):
        self.update_checked_json()

    def update_checked_json(self):
        checked_presets = {}
        root = self.preset_tree_view.invisibleRootItem()

        def collect_checked(item, parent_category=None):
            for i in range(item.childCount()):
                child = item.child(i)
                # If this is a category node
                if child.childCount() > 0:
                    category = child.text(1)
                    collect_checked(child, category)
                else:
                    if child.checkState(0) == Qt.Checked:
                        category = parent_category or child.text(1)
                        preset_name = child.text(2)
                        data = child.data(0, Qt.UserRole)
                        if category not in checked_presets:
                            checked_presets[category] = {}
                        checked_presets[category][preset_name] = data

        collect_checked(root)
        self.checked_json_view.setPlainText(json.dumps(checked_presets, indent=2))

    def populate_detail_table(self, category, preset_name):
        preset_data = CfgMan().get(category).get_preset(preset_name)
        if not isinstance(preset_data, dict):
            self.detail_table.setRowCount(0)
            return
        self.detail_table.blockSignals(True)
        self.detail_table.setRowCount(len(preset_data))
        for row, (key, value) in enumerate(preset_data.items()):
            key_item = QTableWidgetItem(str(key))
            key_item.setFlags(key_item.flags() & ~Qt.ItemIsEditable)
            value_item = QTableWidgetItem(str(value))
            self.detail_table.setItem(row, 0, key_item)
            self.detail_table.setItem(row, 1, value_item)
        # Disconnect previous connections to avoid multiple triggers
        try:
            self.detail_table.itemChanged.disconnect()
        except TypeError:
            pass
        def save_preset_from_table(item):
            data = {}
            for row in range(self.detail_table.rowCount()):
                key_item = self.detail_table.item(row, 0)
                value_item = self.detail_table.item(row, 1)
                if key_item is not None and value_item is not None:
                    data[key_item.text()] = value_item.text()
            CfgMan().get(category).save_preset(preset_name, data)
        self.detail_table.itemChanged.connect(save_preset_from_table)
        self.detail_table.blockSignals(False)

    def on_table_item_changed(self, item):
        selected = self.preset_tree_view.selectedItems()
        if not selected:
            return
        preset_data = selected[0].data(0, Qt.UserRole)
        if not isinstance(preset_data, dict):
            return
        row = item.row()
        key = self.detail_table.item(row, 0).text()
        value = self.detail_table.item(row, 1).text()
        preset_data[key] = value
        selected[0].setData(0, Qt.UserRole, preset_data)
        self.update_checked_json()

    def export_presets(self):
        selected_presets_dict = json.loads(self.checked_json_view.toPlainText())
        path, _ = QFileDialog.getSaveFileName(self, "Export Presets", "", "JSON Files (*.json)")
        if path:
            with open(path, "w") as f:
                json.dump(selected_presets_dict, f, indent=2)

    def import_presets(self):
        path, _ = QFileDialog.getOpenFileName(self, "Import Presets", "", "JSON Files (*.json)")
        if path:
            with open(path, "r") as f:
                imported = json.load(f)
                for category, presets_dict in imported.items():
                    if isinstance(presets_dict, dict):
                        cs_category = CfgMan().get(category)
                        if cs_category is not None:
                            for preset_name, preset_value in presets_dict.items():
                                cs_category.save_preset(preset_name, preset_value)
                self.update_pm_map()
                self.populate_tree()
                self.update_checked_json()
