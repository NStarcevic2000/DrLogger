from PyQt5.QtWidgets import QDialog, QLabel, QHBoxLayout, QVBoxLayout, QComboBox, QPushButton, QApplication, QFileDialog
from PyQt5.QtCore import Qt

import csv
from enum import Enum

from logs_managing.logs_manager import LogsManager
from logs_managing.reserved_names import RESERVED_METADATA_NAMES as RMetaNS

class SAVE_MODE(Enum):
    CLIPBOARD = "Clipboard"
    FILE = "Export to File"

class DELIMITER_TYPES(Enum):
    COMMA = ","
    SEMICOLON = ";"
    SPACE = "SPACE"
    TAB = "TAB"

    @staticmethod
    def get_values():
        return [e.value for e in DELIMITER_TYPES]

class EXPORT_FORMAT(Enum):
    RAW_LOG = "Raw Log"
    RENDERED = "Rendered"
    CSV = "CSV"

    @staticmethod
    def get_values():
        return [e.value for e in EXPORT_FORMAT]


class SaveLogsPrompt(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Save Logs: <UNKNOWN>")
        self.setMinimumSize(200, 200)
        self.main_layout = QVBoxLayout()
        self.main_layout.setAlignment(Qt.AlignTop)
        self.setMinimumWidth(500)
        self.setLayout(self.main_layout)

        self.mode = SAVE_MODE.FILE

        self.selected_rows_label = QLabel("Selected Rows: <UNKNOWN>")
        self.selected_rows_label.setAlignment(Qt.AlignLeft)
        self.main_layout.addWidget(self.selected_rows_label)

        self.selected_mode_label = QLabel("Export Mode: ")
        self.selected_mode_label.setAlignment(Qt.AlignLeft)
        self.selected_mode_selector = QComboBox()
        self.selected_mode_selector.addItems(EXPORT_FORMAT.get_values())
        self.selected_mode_selector.setMinimumWidth(120)
        self.selected_mode_selector.setCurrentIndex(0)
        self.selected_mode_selector.currentIndexChanged.connect(self.show_updated)

        self.delimiter_label = QLabel("Delimiter:")
        self.delimiter_selector = QComboBox()
        self.delimiter_selector.addItems(DELIMITER_TYPES.get_values())
        self.delimiter_selector.setMinimumWidth(80)
        self.delimiter_selector.setCurrentIndex(0)
        self.delimiter_selector.currentIndexChanged.connect(self.show_updated)
        hbox = QHBoxLayout()
        hbox.addWidget(self.selected_mode_label)
        hbox.addWidget(self.selected_mode_selector)
        hbox.addWidget(self.delimiter_label)
        hbox.addWidget(self.delimiter_selector)
        hbox.addStretch()
        self.main_layout.addLayout(hbox)

        self.save_btn = QPushButton("Save")
        self.save_btn.clicked.connect(self.save_clicked)
        self.main_layout.addWidget(self.save_btn)

        self.delimiter = ""
        self.exported_data = []

    def show_updated(self, mode:SAVE_MODE=None, selected_rows:int|list[int]|None=None):
        if mode is not None and isinstance(mode, SAVE_MODE):
            self.mode = mode

        if self.mode == SAVE_MODE.CLIPBOARD:
            self.setWindowTitle("Save Logs: Copy Logs to Clipboard")
            self.save_btn.setText("Copy to Clipboard")
        else:
            self.setWindowTitle("Save Logs: Export Logs to File")
            self.save_btn.setText("Export to File")

        self.update_delimiter()
        self.update_mode()

        data = LogsManager().get_data(rows=selected_rows)
        metadata = LogsManager().get_metadata(rows=selected_rows)
        self.selected_rows_label.setText(f"Selected Rows: {len(data) if data is not None else 'All rows'}")

        idx = self.selected_mode_selector.currentIndex()
        if idx == list(EXPORT_FORMAT).index(EXPORT_FORMAT.RAW_LOG):
            self.exported_data = [dict_item[RMetaNS.General.name][RMetaNS.General.OriginalLogs].get_value() for dict_item in metadata]
        # Export rendered logs (space-separated row values of all data columns)
        elif idx == list(EXPORT_FORMAT).index(EXPORT_FORMAT.RENDERED):
            self.exported_data = [self.delimiter.join(str(cell) for cell in row) for row in data.values.tolist()]
        elif idx == list(EXPORT_FORMAT).index(EXPORT_FORMAT.CSV):
            # Prepare data as list of lists for CSV export
            self.exported_data = [list(row) for row in data]
        if not self.isVisible():
            self.show()

    def save_clicked(self):
        if not self.exported_data or len(self.exported_data) == 0:
            print("No data to export.")
            return
        
        self.update_delimiter()
        self.update_mode()

        export_format = self.selected_mode_selector.currentText()

        if self.mode == SAVE_MODE.FILE:
            file, _ = QFileDialog.getSaveFileName(self, "Save File", "", "All Files (*);;Text Files (*.txt);;CSV Files (*.csv)")
            if file:
                with open(file, 'w', encoding='utf-8', newline='') as f:
                    if export_format == EXPORT_FORMAT.CSV.value:
                        writer = csv.writer(f, delimiter=self.delimiter, quotechar='"', quoting=csv.QUOTE_MINIMAL)
                        for row in self.exported_data:
                            writer.writerow(row)
                        print(f"Exported {len(self.exported_data)} rows to '{file}' as CSV'")
                    else:
                        for line in self.exported_data:
                            f.write(str(line) + "\n")
                        print(f"Exported {len(self.exported_data)} rows to '{file}' as raw text")
        elif self.mode == SAVE_MODE.CLIPBOARD:
            clipboard = QApplication.clipboard()
            if export_format == EXPORT_FORMAT.CSV.value:
                output = []
                for row in self.exported_data:
                    output.append(self.delimiter.join(str(cell) for cell in row))
                clipboard.setText("\n".join(output))
                print(f"Copied {len(self.exported_data)} rows to clipboard as CSV with delimiter '{self.delimiter}'")
            else:
                clipboard.setText("\n".join(str(line) for line in self.exported_data))
                print(f"Copied {len(self.exported_data)} rows to clipboard as raw text")
        self.close()
    
    def update_mode(self):
        idx = self.selected_mode_selector.currentIndex()
        if idx == list(EXPORT_FORMAT).index(EXPORT_FORMAT.RENDERED) or idx == list(EXPORT_FORMAT).index(EXPORT_FORMAT.CSV):
            self.delimiter_label.setVisible(True)
            self.delimiter_selector.setVisible(True)
        elif idx == list(EXPORT_FORMAT).index(EXPORT_FORMAT.RAW_LOG):
            self.delimiter_label.setVisible(False)
            self.delimiter_selector.setVisible(False)

    def update_delimiter(self):
        self.delimiter = self.delimiter_selector.currentText()
        if self.delimiter == "SPACE":
            self.delimiter = " "
        elif self.delimiter == "TAB":
            self.delimiter = "\t"
