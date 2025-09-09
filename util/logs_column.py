from pandas import Series
from typing import Union, List

class DataColumn(Series):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

class MetadataColumn(Series):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

class CollapsingRowsColumn(Series):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

class ConnectionColumn(Series):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

COLUMN_TYPE = Union[DataColumn, MetadataColumn, CollapsingRowsColumn, ConnectionColumn]
ANY_COLUMN_TYPE = List[COLUMN_TYPE]