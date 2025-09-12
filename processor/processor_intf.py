from pandas import DataFrame
from typing import List

from util.logs_column import COLUMN_TYPE
from util.config_store import ConfigStore, Config

class IProcessor():
    def register_config_store(self) -> 'ConfigStore|Config|None':
        return None
    
    def process(self, data: DataFrame) -> 'COLUMN_TYPE|List[COLUMN_TYPE]|None':
        '''
        Process input data and return new columns to be added to LogsManager.
        '''
        return None