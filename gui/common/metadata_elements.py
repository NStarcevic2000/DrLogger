from abc import ABC, abstractmethod
from pandas import DataFrame, Series

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
        total_height = min(5, len(data)) * row_height + 2
        self.element.setMinimumHeight(total_height)
        self.element.setMaximumHeight(total_height)
        # No padding
        self.element.setContentsMargins(0,0,0,0)
        self.data = data
    def get_value(self): return self.data
    def get_widget(self):  return self.element.refresh()