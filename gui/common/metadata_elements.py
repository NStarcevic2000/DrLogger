from abc import ABC, abstractmethod
from pandas import DataFrame, Series

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QLabel
from gui.common.rendered_logs_table import RenderedLogsTable

class MetadataType(ABC):
    @abstractmethod
    def get_value(self):
        pass

    @abstractmethod
    def get_widget(self):
        pass

class MetadataLogLine(MetadataType):
    def __init__(self, data:str, style:Series=None):
        self.element = RenderedLogsTable(DataFrame([data],columns=["Line"]), style=style)
        row_height = self.element.verticalHeader().defaultSectionSize() if hasattr(self.element, 'verticalHeader') else 24
        total_height = 2 * row_height - 2
        self.element.setMinimumHeight(total_height)
        self.element.setMaximumHeight(total_height)
        # No padding
        self.element.setContentsMargins(0,0,0,0)
        self.data = data
    def get_value(self): return self.data
    def get_widget(self): return self.element.refresh()

class MetadataLogsSection(MetadataType):
    def __init__(self, data:DataFrame, style:Series=None, is_iloc:bool=False):
        self.element = RenderedLogsTable(data, style)
        # Set size to fit 5 rows, rest is scrollable
        row_height = self.element.verticalHeader().defaultSectionSize() if hasattr(self.element, 'verticalHeader') else 24
        total_height = min(5, len(data)+1) * row_height + 2
        self.element.setMinimumHeight(total_height)
        self.element.setMaximumHeight(total_height)
        # Enable vertical scrollbar if needed
        self.element.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        # No padding
        self.element.setContentsMargins(0,0,0,0)
        self.data = data
    def get_value(self): return self.data
    def get_widget(self):  return self.element.refresh()

class MetadataColoredLabel(MetadataType):
    def __init__(self, data:str):
        self.data = data
        self.element = QLabel(data)
        # Set foreground to self.data, background to either white or black for best contrast
        def get_contrast_bg(hex_color):
            hex_color = hex_color.lstrip('#')
            if len(hex_color) == 3:
                hex_color = ''.join([c*2 for c in hex_color])
            r, g, b = [int(hex_color[i:i+2], 16) for i in (0, 2, 4)]
            # Calculate luminance
            luminance = 0.299 * r + 0.587 * g + 0.114 * b
            return '#000000' if luminance > 186 else '#FFFFFF'
        bg_color = get_contrast_bg(self.data)
        self.element.setStyleSheet(f"QLabel {{ color : {self.data}; background-color : {bg_color}; }}")
    def get_value(self): return self.data
    def get_widget(self): return self.element