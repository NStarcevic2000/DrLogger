from pandas import DataFrame
from typing import List
from util.singleton import singleton
from util.logs_column import COLUMN_TYPE, ORDERED_COLUMN_TYPES, UNIQUE_NAME_COLUMNS, DataColumn, MetadataColumn, CollapsingRowsColumn

@singleton
class LogsManager():
    ''' Manages special log columns retrieved by ProcessorManager
    '''
    def __init__(self):
        self.columns:List[COLUMN_TYPE] = []

        self.cached_columns: List[COLUMN_TYPE] = []
        # TODO: Is there a better way to handle this? Can't think of any right now.
        self.cached_before_collapsing: tuple[DataFrame, DataFrame] = (DataFrame(), DataFrame())
        ''' Cached data before collapsing rows are applied.'''
        self.cached_fully_rendered: tuple[DataFrame, DataFrame] = (DataFrame(), DataFrame())
        ''' Cached fully rendered data (after collapsing rows are applied).'''

    def erase_data(self):
        self.columns = []
        self.cached_columns = []
        self.cached_before_collapsing = (DataFrame(), DataFrame())
        self.cached_fully_rendered = (DataFrame(), DataFrame())

    def add_new_columns(self, new_columns:List[COLUMN_TYPE]):
        ''' Update the current columns with new columns from a processing stage.'''
        # Check for columns that require unique names and remove old ones
        for col in new_columns:
            if type(col) not in UNIQUE_NAME_COLUMNS:
                self.columns.append(col)
                continue
            for search_col in self.columns:
                if col.name == search_col.name and type(col) == type(search_col):
                    self.columns.remove(search_col)
            self.columns.append(col)
            self.apply_processing(col)

    def apply_processing(self, next_column):
        ''' Apply processing immediately with new columns from a processing stage.
        '''
        # First do for before collapsing
        visible_df, metadata = self.cached_before_collapsing
        visible_df, metadata = next_column.process(
            visible_df.copy(), metadata.copy()
        )
        self.cached_before_collapsing = (visible_df.copy(), metadata.copy())
    
    def apply_post_processing(self):
        ''' Apply post-processing immediately with new columns from a processing stage.
        '''
        if self.cached_columns == self.columns:
            return
        visible_df, metadata = self.cached_before_collapsing
        for column in self.columns:
            visible_df, metadata = column.post_process(
                visible_df.copy(), metadata.copy()
            )
        self.cached_fully_rendered = (visible_df.copy(), metadata.copy())
        # Cache columns
        self.cached_columns = self.columns.copy()

    def __apply_process(self,
                        visible_df: DataFrame,
                        metadata: DataFrame,
                        columns: list[COLUMN_TYPE],
                        ordered_column_types: list[type] = ORDERED_COLUMN_TYPES) -> tuple[DataFrame, DataFrame]:
        ''' Apply processing to all columns.
            @param visible_df: DataFrame with visible data
            @param metadata: DataFrame with metadata
            @param columns: List of columns to process
            @param ordered_column_types: Order in which to apply processing
        '''
        visible_df, metadata = visible_df, metadata
        for col_type in ordered_column_types:
            for col in [x for x in columns if isinstance(x, col_type)]:
                visible_df, metadata = \
                    col.process(visible_df.copy(), metadata.copy())
        return visible_df, metadata

    def __apply_post_process(self,
                             visible_df:DataFrame,
                             metadata:DataFrame,
                             columns:List[COLUMN_TYPE],
                             ordered_column_types:List[type]=ORDERED_COLUMN_TYPES) -> tuple[DataFrame, DataFrame]:
        ''' Apply post-processing to all provided columns.
            @param visible_df: DataFrame with visible data (no metadata columns)
            @param metadata: DataFrame with metadata columns
            @param columns: List of columns to apply post-processing to
            @param ordered_column_types: Order in which to apply post-processing
        '''
        visible_df, metadata = visible_df, metadata
        for col_type in ordered_column_types:
            for col in [x for x in columns if isinstance(x, col_type)]:
                visible_df, metadata = \
                    col.post_process(visible_df.copy(), metadata.copy())
        return visible_df, metadata

    def get_columns(self) -> list[COLUMN_TYPE]:
        return self.columns.copy()

    def get_data(self, rows: int | list[int] | None = None, show_collapsed:bool=False) -> tuple[DataFrame, DataFrame]:
        if show_collapsed:
            self.apply_post_processing()
            visible_df, metadata = self.cached_fully_rendered if show_collapsed else self.cached_before_collapsing
        else:
            visible_df, metadata = self.cached_before_collapsing
        if isinstance(rows, list):
            return visible_df.copy().iloc[rows], metadata.copy().iloc[rows]
        elif isinstance(rows, int):
            return visible_df.copy()[:rows], metadata.copy()[:rows]
        else:
            return visible_df.copy(), metadata.copy()

    # For testing purposes, we might use it somewhere else also
    def simulate_rendered_data(self,
            cols: list[COLUMN_TYPE] | None,
            rows: int | list[int] = DataFrame(),
            starting_visible_df: DataFrame = DataFrame(),
            starting_metadata: DataFrame = DataFrame()) -> DataFrame:
        ''' Simulate the rendering of a DataFrame with given columns and rows.'''
        visible_df = starting_visible_df.copy()
        metadata = starting_metadata.copy()
        # Check columns
        if cols is None or \
                not isinstance(cols, list) or \
                not all(isinstance(col, COLUMN_TYPE) for col in cols):
            raise ValueError("cols must be a list of COLUMN_TYPE or None.")
        if cols is not None:
            visible_df, metadata = self.__apply_process(visible_df.copy(), metadata.copy(), cols)
            visible_df, metadata = self.__apply_post_process(visible_df.copy(), metadata.copy(), cols)
        if isinstance(rows, list):
            return visible_df.iloc[rows]
        elif isinstance(rows, int):
            return visible_df[:rows]
        else:
            return visible_df
