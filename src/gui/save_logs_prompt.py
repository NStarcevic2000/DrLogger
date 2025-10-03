from PyQt5.QtWidgets import QDialog, QLabel, QHBoxLayout, QVBoxLayout, QComboBox, QPushButton, QApplication, QFileDialog
from PyQt5.QtCore import Qt

import csv
from enum import Enum
from pandas import DataFrame

from logs_managing.logs_manager import LogsManager
from logs_managing.reserved_names import RESERVED_METADATA_NAMES as RMetaNS

from util.singleton import singleton

@singleton
class SaveLogsPrompt():
    def save_to_file(self, df:DataFrame|None):
        if not isinstance(df, DataFrame) or df.empty:
            print("No data to export.")
            return
        file, _ = QFileDialog.getSaveFileName(None, "Export to File", "", "Log File (*.log);;CSV File (*.csv)")
        if file:
            with open(file, 'w', encoding='utf-8', newline='') as f:
                if file.endswith('.csv'):
                    df.to_csv(f, index=False)
                    print(f"Exported {len(df)} rows to '{file}' as CSV")
                elif file.endswith('.log'):
                    for line in df.values:
                        f.write(" ".join(str(cell) for cell in line) + "\n")
                    print(f"Exported {len(df)} rows to '{file}' as log")

    def save_to_clipboard(self, df:DataFrame|None):
        if not isinstance(df, DataFrame) or df.empty:
            print("No data to copy.")
            return
        clipboard = QApplication.clipboard()
        clipboard.setText("\n".join([" ".join(str(cell) for cell in line) for line in df.values]))
        print(f"Copied {len(df)} rows to clipboard as log")
