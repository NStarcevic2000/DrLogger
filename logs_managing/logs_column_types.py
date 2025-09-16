from pandas import Series, DataFrame
from typing import Union, List
from typing import final
from enum import Enum

from logs_managing.logs_container import LogsContainer
from logs_managing.reserved_names import RESERVED_COLUMN_NAMES as RColNS
from logs_managing.reserved_names import RESERVED_METADATA_NAMES as RMetaNS

class DataColumn(Series):
    ''' A column that contains visible data for LogsManager table generation.
        It can contain text, numbers, etc. or anything castable to string.
        The dtype must be string.
    '''
    def __init__(self, data, name: str = None):
        if isinstance(data, Series):
            if data.name is not None:
                super().__init__(data[:], name=data.name, dtype="string")
            else:
                super().__init__(data[:], name=name, dtype="string")
        elif isinstance(data, list):
            super().__init__(data[:], name=name, dtype="string")
        else:
            raise ValueError("DataColumn must be initialized with a pandas Series or list.")
        if self.name is None:
            raise ValueError("DataColumn Series must have a name or col_name specified.")
        # Ensure dtype is string
        if self.dtype != "string":
            self[:] = self.astype("string")

    @final
    def process(self, logs_container: LogsContainer):
        print(f"Processing DataColumn: {self.name} with {len(self)} rows. {self.dtype}")
        logs_container.set_data_column(self, self.name)

    @final
    def post_process(self, logs_container: LogsContainer):
        return



class MetadataColumn(Series):
    ''' A column that contains metadata for LogsManager table generation.
        It can contain anything; type is important for details displaying.
    '''
    def __init__(self,
                 data:Series|list,
                 name:str=None,
                 category:str=None):
        # Initialized from Series or list
        if isinstance(data, Series):
            if data.name is not None:
                super().__init__(data, name=data.name)
            elif name is not None:
                super().__init__(data, name=name)
            else:
                raise ValueError("MetadataColumn Series must have a name or col_name specified.")
        elif isinstance(data, list):
            super().__init__(data, name=name)
        else:
            raise ValueError("MetadataColumn must be initialized with a pandas Series or list.")
        
        # Category is just a string, but we can use predefined ones
        self.__category = category if category is not None else \
            RMetaNS.General.name

    @final
    def process(self, logs_container:LogsContainer):
        metadata = Series([{
            self.__category: {
                self.name: row_val
            },
        } for row_val in self.astype(str)], name=self.name)
        logs_container.set_metadata(metadata)
    
    @final
    def post_process(self, logs_container:LogsContainer):
        return



class CaptureMessageColumn(Series):
    ''' A special column for capturing rows of logs into a singular message.\n
        Can be initialized as:\n
        - CaptureMessageColumn(data: Series[str])
            - data: Series of strings to capture messages from. (modified message column with optional NULLs)
            - replace: Ignored
    '''
    def __init__(self,
                 data:Series,
                 name:str,
                 replace:str=None):
        if isinstance(data, Series) and all(isinstance(val, str) or val is None for val in data):
            super().__init__(data, name=name)
        elif isinstance(data, list) and all(isinstance(val, str) or val is None for val in data):
            super().__init__(data, name=name)
        else:
            raise ValueError("CaptureMessageColumn must be initialized with a pandas Series or list.")
        if not all(isinstance(val, str) or val is None for val in self):
            raise ValueError("CaptureMessageColumn Series must contain only strings or None.")
        if self.name is None:
            raise ValueError("CaptureMessageColumn Series must have a name specified.")
        self.__replace = replace

    @final
    def process(self, logs_container:LogsContainer):
        return

    @final
    def post_process(self, logs_container:LogsContainer):
        logs_container.set_collapsable(self.copy(), self.__replace)
        return

# class ConnectionColumn(Series):
#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)


COLUMN_TYPE = Union[DataColumn, MetadataColumn, CaptureMessageColumn]
''' LogsManager column type. '''

ORDERED_COLUMN_TYPES = [DataColumn, MetadataColumn, CaptureMessageColumn]
''' Order in which LogsManager processes column types. '''

UNIQUE_NAME_COLUMNS = [DataColumn]
''' Unique name columns for LogsManager (Cannot have 2 of the same name). '''