from pandas import Series, DataFrame
from typing import Union, List

DEFAULT_MESSAGE_COLUMN = "Message"

class DataColumn(Series):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def post_process(self, visible_data:DataFrame, metadata:DataFrame) -> tuple[DataFrame, DataFrame]:
        visible_data[self.name] = self
        return visible_data, metadata

class MetadataColumn(Series):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def post_process(self, visible_data:DataFrame, metadata:DataFrame) -> tuple[DataFrame, DataFrame]:
        metadata[self.name] = self
        return visible_data, metadata

class CollapsingRowsColumn(Series):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._collapsed_pattern: str|None = None

    def set_heading_pattern(self, pattern: str):
        self._collapsed_pattern = pattern
        return self
    
    def post_process(self, visible_data: DataFrame, metadata: DataFrame) -> tuple[DataFrame, DataFrame]:
        show = self.astype(bool)
        if self._collapsed_pattern is not None:
            hidden_count = 0
            for i in range(len(visible_data)):
                if not show.iat[i]:
                    hidden_count += 1
                    if i + 1 == len(visible_data) or show.iloc[i + 1]:
                        show.iat[i] = True
                        # Clear all columns except DEFAULT_MESSAGE_COLUMN
                        for col in visible_data.columns:
                            visible_data.iat[i, visible_data.columns.get_loc(col)] = ""
                        visible_data.iat[i, visible_data.columns.get_loc(DEFAULT_MESSAGE_COLUMN)] = self._collapsed_pattern.replace("{count}", str(hidden_count))
                        if "Foreground" in metadata.columns:
                            metadata.iat[i, metadata.columns.get_loc("Foreground")] = "gray"
                        if "Background" in metadata.columns:
                            metadata.iat[i, metadata.columns.get_loc("Background")] = "white"
                        hidden_count = 0
                else:
                    hidden_count = 0
        visible_data = visible_data[show]
        metadata = metadata[show]
        visible_data.index = range(len(visible_data))
        metadata.index = range(len(metadata))
        return visible_data, metadata

class ConnectionColumn(Series):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

COLUMN_TYPE = Union[DataColumn, MetadataColumn, CollapsingRowsColumn, ConnectionColumn]
ANY_COLUMN_TYPE = List[COLUMN_TYPE]