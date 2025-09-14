from pandas import Series, DataFrame
from typing import Union, List
from typing import final
from enum import Enum

class PREDEFINED_COLUMN_NAMES(Enum):
    FILE = "File"
    MESSAGE = "Message"
    TIMESTAMP = "Timestamp"
    BACKGROUND = "Background Color"
    FOREGROUND = "Foreground Color"

class PREDEFINED_METADATA_CATEGORIES(Enum):
    GENERAL = "General"

class DataColumn(Series):
    ''' A column that contains visible data LogsManager table generation. 
        It can contain text, numbers, etc. or anything castable to string.
    '''
    def __init__(self, data, name:str=None):
        if isinstance(data, Series):
            if data.name is not None:
                super().__init__(data, name=data.name)
            else:
                super().__init__(data, name=name)
        elif isinstance(data, list):
            super().__init__(data, name=name)
        else:
            raise ValueError("DataColumn must be initialized with a pandas Series or list.")
        if self.name is None:
            raise ValueError("DataColumn Series must have a name or col_name specified.")
        # Convert explicitly to string
        self[:] = self.astype(str).values

    @final
    def process(self, visible_df:DataFrame, metadata:DataFrame) -> DataFrame:
        # Delete previous column
        if self.name in visible_df.columns:
            visible_df.drop(columns=[self.name], inplace=True)
        visible_df[self.name] = self.values.copy()
        return visible_df, metadata

    @final
    def post_process(self, visible_df:DataFrame, metadata:DataFrame) -> tuple[DataFrame, DataFrame]:
        return visible_df, metadata



class MetadataColumn(Series):
    ''' A column that contains metadata for LogsManager table generation.
        It can contain anything; type is important for details displaying.
    '''
    def __init__(self, data, name:str=None,
            category:str=None):
        # Initialized from Series or list
        if isinstance(data, Series):
            if data.name is not None:
                super().__init__(data, name=data.name)
            else:
                super().__init__(data, name=name)
        elif isinstance(data, list):
            super().__init__(data, name=name)
        else:
            raise ValueError("MetadataColumn must be initialized with a pandas Series or list.")
        
        # Category is just a string, but we can use predefined ones
        self.__category = category if category is not None else \
            PREDEFINED_METADATA_CATEGORIES.GENERAL.value

    @final
    def process(self, rendered_data:DataFrame, metadata:DataFrame) -> tuple[DataFrame, DataFrame]:
        # Delete previous column
        if self.name in metadata.columns:
            metadata.drop(columns=[self.name], inplace=True)
        metadata[self.name] = [
            {
                self.__category: {
                    self.name: value
                }
            } for value in self.values.copy()]
        return rendered_data.copy(), metadata.copy()
    
    @final
    def post_process(self, visible_data:DataFrame, metadata:DataFrame) -> tuple[DataFrame, DataFrame]:
        return visible_data.copy(), metadata.copy()



class CollapsingRowsColumn(Series):
    ''' A boolean column that indicates whether the corresponding row should be shown or collapsed.
        If collapsed [cell value True], the row is hidden from visible_data DataFrame.
    '''
    def __init__(self, data, name:str=None,
            collapse_heading_pattern:str=None):
        # Initialized from Series or list
        if isinstance(data, Series) and all(isinstance(x, bool) for x in data):
            if data.name is not None:
                super().__init__(data, name=data.name)
            else:
                super().__init__(data, name=name)
        elif isinstance(data, list) and all(isinstance(x, bool) for x in data):
            super().__init__(data, name=name)
        else:
            raise ValueError("MetadataColumn must be initialized with a pandas Series or list.")
        
        self.collapse_heading_pattern: str|None = collapse_heading_pattern

    @final
    def process(self, rendered_data:DataFrame, metadata:DataFrame) -> tuple[DataFrame, DataFrame]:
        return rendered_data, metadata

    @final
    def post_process(self, visible_data: DataFrame, metadata: DataFrame) -> tuple[DataFrame, DataFrame]:
        show = self.astype(bool).copy()
        if self.collapse_heading_pattern is not None:
            # If there is a collapse pattern, insert a heading row for each group of collapsed rows
            hidden_count = 0
            for i in range(len(visible_data)):
                if not show.iat[i]:
                    hidden_count += 1
                    if i + 1 == len(visible_data) or show.iloc[i + 1]:
                        show.iat[i] = True
                        # Clear all columns except MESSAGE and set it to the collapsed pattern
                        for col in visible_data.columns:
                            if col != PREDEFINED_COLUMN_NAMES.MESSAGE.value:
                                visible_data.iat[i, visible_data.columns.get_loc(col)] = ""
                        visible_data.iat[i, visible_data.columns.get_loc(PREDEFINED_COLUMN_NAMES.MESSAGE.value)] = self.collapse_heading_pattern.replace("{count}", str(hidden_count))
                        if PREDEFINED_COLUMN_NAMES.FOREGROUND.value in metadata.columns:
                            metadata.iat[i, metadata.columns.get_loc(PREDEFINED_COLUMN_NAMES.FOREGROUND.value)] = "#7F7F7F"
                        if PREDEFINED_COLUMN_NAMES.BACKGROUND.value in metadata.columns:
                            metadata.iat[i, metadata.columns.get_loc(PREDEFINED_COLUMN_NAMES.BACKGROUND.value)] = "#FFFFFF"
                        hidden_count = 0
                else:
                    hidden_count = 0
            visible_data = visible_data[show.values]
            visible_data.index = range(len(visible_data))
            if metadata is not None and not metadata.empty:
                metadata = metadata[show.values]
                metadata.index = range(len(metadata))
        else:
            # If no collapse pattern, just filter out hidden rows
            visible_data = visible_data[show.values]
            visible_data.index = range(len(visible_data))
            if metadata is not None and not metadata.empty:
                metadata = metadata[show.values]
                metadata.index = range(len(metadata))
        return visible_data, metadata

# class ConnectionColumn(Series):
#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)


COLUMN_TYPE = Union[DataColumn, MetadataColumn, CollapsingRowsColumn]
''' LogsManager column type. '''

ORDERED_COLUMN_TYPES = [DataColumn, MetadataColumn, CollapsingRowsColumn]
''' Order in which LogsManager processes column types. '''

UNIQUE_NAME_COLUMNS = [DataColumn, MetadataColumn]
''' Unique name columns for LogsManager (Cannot have 2 of the same name). '''