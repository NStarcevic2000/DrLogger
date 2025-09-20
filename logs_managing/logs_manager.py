from pandas import DataFrame, Series
from typing import List
from util.singleton import singleton
from logs_managing.logs_column_types import COLUMN_TYPE, ORDERED_COLUMN_TYPES, UNIQUE_NAME_COLUMNS
from logs_managing.logs_container import LogsContainer

@singleton
class LogsManager():
    ''' Manages special log columns retrieved by ProcessorManager
    '''
    def __init__(self):
        self.columns:List[COLUMN_TYPE] = []
        self.logs_container = LogsContainer()

    def erase_data(self):
        self.columns = []
        self.logs_container.clear()

    def add_new_columns(self, new_columns:List[COLUMN_TYPE]):
        ''' Update the current columns with new columns from a processing stage.'''
        for col in new_columns:
            self.columns.append(col)
            print(f"Added column '{col.name}' of type {col.__class__.__name__}")
        self.__apply_process(new_columns)
    
    def finalize(self):
        ''' Finalize the logs data after all processing is done.'''
        self.__apply_post_process(self.columns)

    def __apply_process(self,
                        columns: list[COLUMN_TYPE],
                        logs_container: LogsContainer = None,
                        ordered_column_types: list[type] = ORDERED_COLUMN_TYPES):
        ''' Apply processing to all columns.
            @param visible_df: DataFrame with visible data
            @param metadata: DataFrame with metadata
            @param columns: List of columns to process
            @param ordered_column_types: Order in which to apply processing
        '''
        print(f"Applying processing for columns:{[col.name for col in columns]}")
        for col_type in ordered_column_types:
            for col in [x for x in columns if isinstance(x, col_type)]:
                print(f"Processing column '{col.name}' of type {col.__class__.__name__}")
                col.process(logs_container) if logs_container is not None else col.process(self.logs_container)

    def __apply_post_process(self,
                             columns: list[COLUMN_TYPE],
                             logs_container: LogsContainer = None,
                             ordered_column_types: list[type] = ORDERED_COLUMN_TYPES):
        ''' Apply post-processing to all provided columns.
            @param visible_df: DataFrame with visible data (no metadata columns)
            @param metadata: DataFrame with metadata columns
            @param columns: List of columns to apply post-processing to
            @param ordered_column_types: Order in which to apply post-processing
        '''
        for col_type in ordered_column_types:
            for col in [x for x in columns if isinstance(x, col_type)]:
                col.post_process(logs_container) if logs_container is not None else  col.post_process(self.logs_container)

    def get_columns(self) -> list[COLUMN_TYPE]:
        return self.columns.copy()

    def get_data(self,
                 rows: int | list[int] = None):
        return self.logs_container.get_data(rows)
    
    def get_metadata(self,
                     rows: int | list[int] = None):
        return self.logs_container.get_metadata(rows)

    def get_style(self,
                   rows: int | list[int] = None):
        return self.logs_container.get_style(rows)

    def get_all_packaged(self,
                 rows: int | list[int] = None):
        return (
            self.logs_container.get_data(rows),
            self.logs_container.get_metadata(rows)
        )

    # For testing purposes, we might use it somewhere else also
    def simulate_rendered_data(self,
            cols: list[COLUMN_TYPE] | None,
            rows: int | list[int] = None) -> DataFrame:
        ''' Simulate the rendering of a DataFrame with given columns and rows.'''
        logs_container = LogsContainer()
        # Check columns
        if cols is None or \
                not isinstance(cols, list) or \
                not all(isinstance(col, COLUMN_TYPE) for col in cols):
            raise ValueError("cols must be a list of COLUMN_TYPE or None.")
        # Apply processing
        self.__apply_process(cols, logs_container=logs_container)
        # Apply post-processing
        self.__apply_post_process(cols, logs_container=logs_container)
        return logs_container.get_data(rows)
