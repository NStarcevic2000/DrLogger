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
        return pd.concat(visible_cols, axis=1).copy()

    def get_metadata(self, rows: int | None = None) -> DataFrame:
        metadata_cols = [col[:rows] for col in self.columns if col.__class__ == MetadataColumn]
        if not metadata_cols:
            return pd.DataFrame()
        return pd.concat(metadata_cols, axis=1).copy()
    
    def get_collapsing_rows(self, rows: int | None = None) -> DataFrame:
        collapsing_rows_cols = [col[:rows] for col in self.columns if col.__class__ == CollapsingRowsColumn]
        if not collapsing_rows_cols:
            return pd.DataFrame()
        return pd.concat(collapsing_rows_cols, axis=1).copy()

    def get_columns(self) -> list[COLUMN_TYPE]:
        return self.columns
    
    def post_process_by_column(self,
        cols: list[COLUMN_TYPE],
        visible_data: DataFrame,
        metadata: DataFrame) -> tuple[DataFrame, DataFrame]:

        # Process DataColumns
        # In case original DataFrame has some of the columns, we want to replace them with the new DataColumn values
        for col in [x for x in cols if isinstance(x, DataColumn)]:
            if col.name in visible_data.columns:
                del visible_data[col.name]
            visible_data[col.name] = col
        
        # Process MetadataColumns
        # In case original DataFrame has some of the columns, we want to replace them with the new DataColumn values
        for col in [x for x in cols if isinstance(x, MetadataColumn)]:
            if col.name in metadata.columns:
                del metadata[col.name]
            metadata[col.name] = col

        # Process CollapsingRowsColumns
        for col in [x for x in cols if isinstance(x, CollapsingRowsColumn)]:
            visible_data, metadata = col.post_process(visible_data.copy(), metadata.copy())

        return visible_data, metadata

    def get_rendered_data(self, rows: int | None = None) -> tuple[DataFrame, DataFrame]:
        visible_data = self.get_visible_data(rows)
        metadata = self.get_metadata(rows)
        visible_data, metadata = self.post_process_by_column(self.columns, visible_data.copy(), metadata.copy())
        return visible_data, metadata

    # For testing purposes, we might use it somewhere else also
    def simulate_rendered_data(self,
            cols: list[COLUMN_TYPE] | None,
            rows: int | None = None,
            visible_df: DataFrame | None = None) -> DataFrame:
        
        visible_df = DataFrame() if visible_df is None else visible_df
        
        visible_df = DataFrame() if visible_df is None else visible_df
        # Return early if no columns to process
        if cols is None or len(cols) == 0:
            return visible_df
        visible_df, _ = self.post_process_by_column(cols, visible_df.copy(), DataFrame())
        return visible_df[:rows] if rows is not None else visible_df
