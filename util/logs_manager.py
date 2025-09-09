import pandas as pd
from pandas import DataFrame
from util.singleton import singleton
from util.logs_column import COLUMN_TYPE, DataColumn, MetadataColumn, CollapsingRowsColumn, ConnectionColumn

DEFAULT_MESSAGE_COLUMN = "Message"

@singleton
class LogsManager():
    def __init__(self):
        self.columns:list[COLUMN_TYPE] = []
        self.cached_data = None  # Invalidate cached data

    def erase_data(self):
        self.columns = []
        self.cached_data = None

    def update_data(self, new_data:list[COLUMN_TYPE]|COLUMN_TYPE):
        new_columns = new_data if isinstance(new_data, list) else [new_data]
        if self.columns is None or self.columns == []:
            self.columns = new_columns
            return
        # Remove all previous columns with the same name as any of the new columns
        new_column_names = [col.name for col in new_columns]
        self.columns = [col for col in self.columns if col.name not in new_column_names]
        # Only then add the new columns
        self.columns.extend(new_columns)

    def get_data(self, rows: int | None = None) -> DataFrame:
        cols = [col[:rows] for col in self.columns]
        return pd.concat(cols, axis=1)

    def get_visible_data(self, rows: int | None = None) -> DataFrame:
        visible_cols = [col[:rows] for col in self.columns if col.__class__ == DataColumn]
        if not visible_cols:
            return pd.DataFrame()
        return pd.concat(visible_cols, axis=1)

    def get_metadata(self, rows: int | None = None) -> DataFrame:
        metadata_cols = [col[:rows] for col in self.columns if col.__class__ == MetadataColumn]
        if not metadata_cols:
            return pd.DataFrame()
        return pd.concat(metadata_cols, axis=1)
    
    def get_collapsing_rows(self, rows: int | None = None) -> DataFrame:
        collapsing_rows_cols = [col[:rows] for col in self.columns if col.__class__ == CollapsingRowsColumn]
        if not collapsing_rows_cols:
            return pd.DataFrame()
        return pd.concat(collapsing_rows_cols, axis=1)

    def get_columns(self) -> list[COLUMN_TYPE]:
        return self.columns
    
    def get_rendered_data(self, rows: int | None = None) -> tuple[DataFrame, DataFrame]:
        visible_data = self.get_visible_data(rows).copy()
        metadata = self.get_metadata(rows).copy()
        for col in [col for col in self.columns if col.__class__ == CollapsingRowsColumn]:
            print(f"Applying post_process for column: {col.name}")
            visible_data, metadata = col.post_process(visible_data, metadata)
        return visible_data, metadata
