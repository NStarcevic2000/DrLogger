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
    

class MetadataLogsSection(MetadataType):
    def __init__(self, data:DataFrame, style:Series, is_iloc:bool=False):
        self.element = RenderedLogsTable(data, style)
        self.data = data
    def get_value(self): return self.data
    def get_widget(self):  return self.element