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

    # For testing purposes, we might use it somewhere else also
    def simulate_rendered_data_for_cols(self, cols: list[COLUMN_TYPE]|None, rows: int | None = None) -> DataFrame:
        ret_df = DataFrame()
        if cols is None or len(cols) == 0:
            return DataFrame()
        # Collect all DataColumn names to preserve columns even if empty
        data_col_names = [col.name for col in cols if col.__class__ == DataColumn]
        for col in [col for col in cols if col.__class__ == DataColumn]:
            if col.name in ret_df.columns:
                raise ValueError(f"Duplicate column name detected: {col.name}")
            ret_df[col.name] = col
        for col in [col for col in cols if col.__class__ == CollapsingRowsColumn]:
            ret_df, _ = col.post_process(ret_df, DataFrame())
        # Remove all empty rows, but preserve columns
        ret_df.replace("", pd.NA, inplace=True)
        ret_df.dropna(how='all', inplace=True)
        # Ensure columns are present even if DataFrame is empty
        for col_name in data_col_names:
            if col_name not in ret_df.columns:
                ret_df[col_name] = pd.Series(dtype="object")
        ret_df = ret_df[data_col_names]  # preserve column order
        ret_df.reset_index(drop=True, inplace=True)
        return ret_df[:rows] if rows is not None else ret_df
