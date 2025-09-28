from pandas import DataFrame, Series, concat
import pandas

from util.dict_merge import merge_dicts, overlay_dict

from logs_managing.reserved_names import RESERVED_COLUMN_NAMES as RColNameNS
from logs_managing.reserved_names import RESERVED_METADATA_NAMES as RMetaNS

from gui.common.metadata_elements import MetadataLogsSection

class LogsContainer():
    ''' Container for both data and all its related properties and details. '''
    def __init__(self):
        self.clear()
    
    def clear(self):
        self.data = DataFrame()
        self.metadata = Series([], name="METADATA")
        self.visible_rows = Series([], dtype=bool).tolist()
        return self

    def set_data_column(self, column:Series, name:str):
        print(f"Setting data column '{name}'")
        ''' Set or update the main data DataFrame. '''
        if not isinstance(column, Series) or column.dtype != "string":
            raise ValueError("column must be a pandas Series of strings.")
        elif self.data.empty:
            self.data = DataFrame(column, columns=[name]).copy()
        elif len(column) != len(self.data):
            raise ValueError("New data must have the same number of rows as existing data.")
        else:
            self.data[name] = column.copy()
            self.data = self.data[[col for col in self.data.columns if col != name] + [name]]
            
        # Initialize other elements
        if self.metadata.empty:
            self.metadata = Series([{}]*len(self.data), name="METADATA")
        if self.visible_rows == []:
            self.visible_rows = Series([True]*len(self.data), dtype=bool).tolist()
        return self

    def get_data(self, row:int|list[int]=None, show_collapsed:bool=True) -> DataFrame:
        if row is None:
            return self.data[self.visible_rows].copy() if show_collapsed else \
                self.data.copy()
        elif isinstance(row, int):
            return self.data[self.visible_rows].copy().head(row) if show_collapsed else \
                self.data.copy().head(row)
        elif isinstance(row, list):
            return self.data[self.visible_rows].loc[row].copy() if show_collapsed else \
                self.data.loc[row].copy()
        else:
            raise ValueError("Invalid row index type.")
        
    def get_data_columns(self) -> list[str]:
        return self.data.columns.tolist()





    def set_metadata(self, metadata:Series):
        ''' Set or update the metadata Series. '''
        if self.data.empty:
            raise ValueError("Data must be set before setting metadata.")
        elif len(metadata) != len(self.data):
            raise ValueError("New metadata must have the same number of rows as existing data.")
        elif metadata.dtype != dict:
            raise ValueError("Metadata must be a pandas Series of dictionaries.")
        elif self.data.empty:
            raise ValueError("Data must be set before setting metadata.")
        elif len(metadata) != len(self.data):
            raise ValueError("New metadata must have the same number of rows as existing data.")
        elif self.metadata.empty:
            self.metadata = metadata.copy()
        else:
            self.metadata = self.metadata.copy().combine(metadata.copy(), merge_dicts)
        if self.visible_rows == []:
            self.visible_rows = Series([True]*len(self.data), dtype=bool).tolist()
        return self

    def get_metadata(self, row:int|list[int]=None, show_collapsed:bool=True) -> Series:
        if row is None:
            return self.metadata[self.visible_rows].copy() if show_collapsed else \
                self.metadata.copy()
        elif isinstance(row, int):
            return self.metadata[self.visible_rows].copy().head(row) if show_collapsed else \
                self.metadata.copy().head(row)
        elif isinstance(row, list):
            return self.metadata[self.visible_rows].loc[row].copy() if show_collapsed else \
                self.metadata.loc[row].copy()
        else:
            raise ValueError("Invalid row index type.")





    def set_style(self, style:Series):
        ''' Populate specific fields in Metadata for Styling purposes.'''
        if self.data.empty:
            raise ValueError("Data must be set before setting style.")
        elif len(style) != len(self.data):
            raise ValueError("New style must have the same number of rows as existing data.")
        elif style.dtype != dict:
            raise ValueError("Style must be a pandas Series of dictionaries.")
        elif self.metadata.empty:
            self.metadata = style.copy()
        else:
            style_column = Series({
                    RMetaNS.General.name: {
                    RMetaNS.General.ForegroundColor: "#000000",
                    RMetaNS.General.BackgroundColor: "#FFFFFF",
                    RMetaNS.General.FontStyle: "normal",
                }
            }*len(self.data), name="Style")
            overlayed_style_column = style_column.combine(style, overlay_dict)
            if overlayed_style_column != self.metadata:
                print("Warning: Nothing has changed, make sure it is intended or that the keys are formatted as expected.")
                return self
            self.metadata = self.metadata.combine(overlayed_style_column, merge_dicts)
        return self

    def get_style(self, row:int|list[int]=None, show_collapsed:bool=True) -> Series:
        style_column = Series([{
            RMetaNS.General.name: {
                RMetaNS.General.ForegroundColor: "#000000",
                RMetaNS.General.BackgroundColor: "#FFFFFF"
            }
            }]*len(self.metadata), index=self.metadata.index, name="Style")
        style_column = style_column.copy().combine(self.metadata.copy(), overlay_dict)
        if row is None:
            return style_column[self.visible_rows] if show_collapsed else style_column
        elif isinstance(row, int):
            return style_column[self.visible_rows].head(row) if show_collapsed else \
                style_column.head(row)
        elif isinstance(row, list):
            return style_column[self.visible_rows].loc[row] if show_collapsed else \
                style_column.loc[row]
        else:
            raise ValueError("Invalid row index type.")





    def __capture(self,
                  captured_header_idx:int,
                  captured_header_repl:str,
                  captured_data:DataFrame,
                  ):
        # print(f"Captured:\n{captured_data}\nWith metadata:\n{captured_metadata}")
        first_row, last_row = captured_data.index[0], captured_data.index[-1]
        # print(f"Before capture, data is:\n{self.data}\nWith metadata:\n{self.metadata}")
        # If we do not have some of the rows in data, we must have captured them already
        #TODO: This check is too strict, we can capture rows that are not in data if they were captured before
        valid_indices = [idx for idx in captured_data.index if idx in self.data.index]
        if not valid_indices:
            # If nothing left to capture, just return
            return
        captured_data = captured_data.loc[valid_indices]
        first_row, last_row = captured_data.index[0], captured_data.index[-1]
        # Format captured header
        captured_header_repl = captured_header_repl.replace("{count}", str(len(captured_data)))
        # Merge generated metadata with existing metadata
        # TODO: Figure out a different way to merge metadata, this is too strict
        self.metadata.at[captured_header_idx] = merge_dicts(self.metadata.at[captured_header_idx],
        {
            RMetaNS.General.name: {
                RMetaNS.General.ForegroundColor: "#878787",
                RMetaNS.General.BackgroundColor: "#FFFFFF",
            },
            RMetaNS.CaptureRows.name: {
                RMetaNS.CaptureRows.CaptureRows: MetadataLogsSection(captured_data, self.metadata[captured_data.index.to_list()]),
                RMetaNS.CaptureRows.FromToIndexes: f"Lines {first_row} to {last_row}",
                RMetaNS.CaptureRows.CollapsedInTotal: len(captured_data)
            }
        })
        # Set header row
        self.data.at[captured_header_idx, RColNameNS.Message] = captured_header_repl
        # Hide captured rows
        for idx in captured_data.index:
            self.visible_rows[idx] = False
        # Unhide header row
        self.visible_rows[captured_header_idx] = True
        # print(f"After capture, data is:\n{self.data}\nWith metadata:\n{self.metadata} and visible_rows:\n{self.visible_rows}\n")

    def set_collapsable(self, collapsable:Series, replace:str=None):
        ''' Set or update the collapsable Series.'''
        class CapturedData:
            def __init__(self):
                self.reset()

            def reset(self):
                self.header_idx = None
                self.header_fmt = None
                self.begin_idx = None
                self.end_idx = None

        captured_data = CapturedData()
        if len(self.data[RColNameNS.Message]) != len(collapsable):
            raise ValueError("collapsable Series must have the same length as the data Message column.")
        for row_idx in self.data.index:
            orig_message = self.data.at[row_idx, RColNameNS.Message]
            new_message = collapsable.at[row_idx]
            # No changes, see if we captured anything
            if orig_message == new_message:
                # We did capture something, save it
                if captured_data.begin_idx is not None and captured_data.end_idx is not None:
                    self.__capture(
                        captured_data.begin_idx if captured_data.header_idx is None else captured_data.header_idx,
                        replace if captured_data.header_fmt is None else captured_data.header_fmt,
                        self.data.loc[captured_data.begin_idx:captured_data.end_idx].copy(),
                    )
                    # Reset captured data and metadata
                    captured_data.reset()
            
            # Modified message indicates start of capture group
            elif new_message != None:
                # Save new message as a header for Message column
                captured_data.header_idx, captured_data.header_fmt = row_idx, new_message
                # Capture data and metadata
                captured_data.begin_idx, captured_data.end_idx = row_idx if captured_data.begin_idx is None else captured_data.begin_idx, row_idx
            
            # None is the continuation of a capture
            # If replace is defined, it can also be the start of a capture group
            elif new_message is None:
                # Capture data and metadata
                captured_data.begin_idx, captured_data.end_idx = row_idx if captured_data.begin_idx is None else captured_data.begin_idx, row_idx
        # Capture very end if any is left
        if captured_data.begin_idx is not None and captured_data.end_idx is not None:
            self.__capture(
                captured_data.begin_idx if captured_data.header_idx is None else captured_data.header_idx,
                replace if captured_data.header_fmt is None else captured_data.header_fmt,
                self.data.loc[captured_data.begin_idx:captured_data.end_idx].copy(),
            )
        return self
