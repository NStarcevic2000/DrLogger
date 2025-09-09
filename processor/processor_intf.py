from pandas import DataFrame

from util.logs_column import DataColumn, MetadataColumn, CollapsingRowsColumn, ConnectionColumn
from util.config_store import ConfigStore, Config

type ANY_COLUMN_TYPE = DataColumn|MetadataColumn|CollapsingRowsColumn|ConnectionColumn

DEFAULT_MESSAGE_COLUMN = "Message"

class IProcessor():
    def register_config_store(self) -> 'ConfigStore|Config|None':
        return None
    
    def process(self, data) -> list[ANY_COLUMN_TYPE]|None:
        return None