from PyQt5.QtWidgets import QHBoxLayout, QVBoxLayout, QLabel, QPushButton, QMessageBox, QTableWidget, QTableWidgetItem, QLineEdit, QFrame
from PyQt5.QtGui import QIntValidator
from PyQt5.QtCore import Qt

from processor.colorLogsProc import ColorLogsUtils

from pandas import DataFrame

class PreviewLogsSection(QVBoxLayout):
    def __init__(self, parent, configStore:None, pipeline=None):
        super().__init__()
        self.cs = configStore
        self.parent = parent
        self.pipeline = pipeline
        self.clu = ColorLogsUtils(self.cs)

        # Add separator
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Sunken)
        self.addWidget(separator)
        
        self.label = QLabel("Preview:")

        self.preview_button = QPushButton("Preview")
        self.preview_button.clicked.connect(self.preview_logs_cmd)
        self.preview_button.setFixedSize(self.preview_button.sizeHint())

        hbox = QHBoxLayout()
        hbox.addWidget(self.label)
        hbox.addWidget(self.preview_button)
        self.addLayout(hbox)
        
        self.preview_logs_table = QTableWidget()
        self.preview_logs_table.setColumnCount(1)  # Example: 3 columns for preview
        self.preview_logs_table.setHorizontalHeaderLabels(["No Data",])
        self.preview_logs_table.setRowCount(5)  # Example: 5 rows for preview
        # Set maximum height to fit 6 rows
        row_height = self.preview_logs_table.verticalHeader().defaultSectionSize()
        header_height = self.preview_logs_table.horizontalHeader().height()
        self.preview_logs_table.setMaximumHeight(header_height + row_height * 5 + 4)

        vbox = QVBoxLayout()

        self.preview_lines_label = QLabel("Preview lines:")
        self.preview_lines_label.setAlignment(Qt.AlignRight)
        self.preview_lines_edit = QLineEdit()
        self.preview_lines_edit.setPlaceholderText("Enter number of lines to preview")
        self.preview_lines_edit.setFixedWidth(50)
        self.preview_lines_edit.setAlignment(Qt.AlignRight)
        # Limit to only set numbers
        self.preview_lines_edit.setValidator(QIntValidator(1, 1000, self.parent))
        self.preview_lines_edit.setText(
            str(self.cs.get(self.cs.r.preferences.preview_max_lines, 5))
        )  # Default to 5 lines
        self.preview_lines_edit.textChanged.connect(
            lambda text: self.cs.set(self.cs.r.preferences.preview_max_lines, int(text)) if text.isdigit() else None
        )
        
        hbox = QHBoxLayout()
        hbox.addWidget(self.preview_lines_label)
        hbox.addWidget(self.preview_lines_edit)
        hbox.setAlignment(Qt.AlignRight)
        vbox.addLayout(hbox)
        vbox.setAlignment(Qt.AlignTop)

        # Expand the table maximally
        self.preview_logs_table.horizontalHeader().setStretchLastSection(True)

        hbox = QHBoxLayout()
        hbox.addWidget(self.preview_logs_table, stretch=1)
        hbox.addLayout(vbox)
        self.addLayout(hbox)

        # Set this layout to the bottom of the parent layout
        self.setAlignment(Qt.AlignBottom)

    def setState(self, enabled=True):
        self.label.setEnabled(enabled)
        # Commented out as these attributes are not defined in this class
        # self.choose_preset_label.setEnabled(enabled)
        # self.choose_preset_combobox.setEnabled(enabled)
    
    def preview_logs_cmd(self):
        self.pipeline.run()
        self.update()
    
    def update(self):
        max_lines = max(1, self.cs.get(self.cs.r.preferences.preview_max_lines, 5))
        # Populate the preview table with DataFrame passed from the pipeline
        if self.pipeline:
            logs = self.pipeline.get_data().head(max_lines)
            if logs is not None and isinstance(logs, DataFrame) and not logs.empty:
                num_rows = logs.shape[0]
                num_cols = logs.shape[1]
                self.preview_logs_table.setRowCount(num_rows)
                self.preview_logs_table.setColumnCount(num_cols)
                try:
                    header_labels = [str(col) for col in logs.columns]
                except Exception:
                    header_labels = [f"Column {i+1}" for i in range(num_cols)]
                self.preview_logs_table.setHorizontalHeaderLabels(header_labels)
                for i in range(num_rows):
                    for j in range(num_cols):
                        value = logs.iat[i, j]
                        item = QTableWidgetItem(str(value))
                        self.preview_logs_table.setItem(i, j, item)
                
                # Apply colors after all items are created
                color_metadata = self.pipeline.get_color_metadata().head(max_lines)
                if not color_metadata.empty and len(color_metadata) == num_rows:
                    self.clu.update_colors(self.preview_logs_table, color_metadata)
                
                # Set column resize modes: all columns except last are compressed, last is stretch
                header = self.preview_logs_table.horizontalHeader()
                for col in range(num_cols - 1):
                    header.setSectionResizeMode(col, header.ResizeToContents)
                if num_cols > 0:
                    header.setSectionResizeMode(num_cols - 1, header.Stretch)
            else:
                self.preview_logs_table.setRowCount(0)
                self.preview_logs_table.setColumnCount(0)
        else:
            if self.parent is not None:
                QMessageBox.warning(self.parent, "Warning", "Pipeline is not set. Cannot update preview logs.")