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
        # Remove all previous columns with the same name as any of the new columns
        new_column_names = [col.name for col in new_columns]
        self.columns = [col for col in self.columns if col.name not in new_column_names]
        # Only then add the new columns
        self.columns.extend(new_columns)

    def get_data(self, rows: int | None = None) -> DataFrame:
        if self.cached_data is not None:
            return self.cached_data
        cols = [col[:rows] for col in self.columns]
        return pd.concat(cols, axis=1)

    def get_visible_data(self, rows: int | None = None) -> DataFrame:
        visible_cols = [col[:rows] for col in self.columns if col.__class__ == DataColumn]
        if not visible_cols:
            return pd.DataFrame()
        return pd.concat(visible_cols, axis=1)

    def get_metadata(self, rows: int | None = None) -> DataFrame:
        metadata_cols = [col for col in self.columns if col.__class__ == MetadataColumn]
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
    
    def get_rendered_data(self, rows: int | None = None) -> DataFrame:
        rendered_data = self.get_visible_data(rows).copy()
        metadata = self.get_metadata(rows).copy()
        collapsed_rows = self.get_collapsing_rows(rows).copy()

        rendered_data.fillna("", inplace=True)
        # Hide all rows that are marked as hidden in collapsing rows columns
        hidden_count = 0
        for i in range(len(rendered_data)):
            if not collapsed_rows.iloc[i]["show"]:
                hidden_count += 1
                # If next row is shown or end of data, mark this row
                if i + 1 == len(rendered_data) or collapsed_rows.iloc[i + 1]["show"]:
                    collapsed_rows.at[i, "show"] = True
                    # All other columns should be set to empty
                    for col in rendered_data.columns:
                        if col != "show":
                            rendered_data.at[i, col] = ""
                    row_word = "row" if hidden_count == 1 else "rows"
                    rendered_data.at[i, DEFAULT_MESSAGE_COLUMN] = f"< filtered {hidden_count} {row_word} >"
                    metadata.at[i, "Foreground"] = "gray"
                    metadata.at[i, "Background"] = "white"
                    hidden_count = 0
            else:
                hidden_count = 0
        # Filter rows but keep original indexing
        mask = collapsed_rows["show"]
        rendered_data = rendered_data[mask]
        metadata = metadata[mask]
        rendered_data.index = range(len(rendered_data))
        metadata.index = range(len(metadata))
        return rendered_data, metadata
