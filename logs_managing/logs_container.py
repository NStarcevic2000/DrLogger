from pandas import DataFrame, Series, concat
import pandas

from util.dict_merge import merge_dicts, overlay_dict

from logs_managing.reserved_names import RESERVED_COLUMN_NAMES as RColNameNS
from logs_managing.reserved_names import RESERVED_METADATA_NAMES as RMetaNS

class LogsContainer():
    ''' Container for both data and all its related properties and details. '''
    def __init__(self):
        self.data = DataFrame()
        self.metadata = Series([], name="METADATA")
        self.captured_rows = Series([], name="COLLAPSABLE")
    
    def clear(self):
        self.data = DataFrame()
        self.metadata = Series([], name="METADATA")
        self.captured_rows = Series([], name="COLLAPSABLE")
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
            self.data = self.data.drop(columns=[name], errors='ignore')
            self.data[name] = column.copy()
        if self.metadata.empty:
            self.metadata = Series([{}]*len(self.data), name="METADATA")
        if self.captured_rows.empty:
            self.captured_rows = Series([None] * len(self.data), index=self.data.index, name="COLLAPSABLE", dtype="object")
        return self
    
    def get_data(self, row:int|list[int]=None) -> DataFrame:
        if row is None:
            return self.data.copy()
        elif isinstance(row, int):
            return self.data.copy().head(row)
        elif isinstance(row, list):
            return self.data.loc[row].copy()
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
        return self
    
    def get_metadata(self, row:int|list[int]=None) -> Series:
        if row is None:
            return self.metadata.copy()
        elif isinstance(row, int):
            return self.metadata.copy().head(row)
        elif isinstance(row, list):
            return self.metadata.loc[row].copy()
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

    def get_style(self, row:int|list[int]=None) -> Series:
        style_column = Series([{
            RMetaNS.General.name: {
                RMetaNS.General.ForegroundColor: "#000000",
                RMetaNS.General.BackgroundColor: "#FFFFFF"
            }
            }]*len(self.metadata), index=self.metadata.index, name="Style")
        style_column = style_column.copy().combine(self.metadata.copy(), overlay_dict)
        if row is None:
            return style_column
        elif isinstance(row, int):
            return style_column.copy().head(row)
        elif isinstance(row, list):
            return style_column.loc[row].copy()
        else:
            raise ValueError("Invalid row index type.")
    





    def __capture(self,
                  captured_header:tuple[int, str],
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
        # In case of uniform capturing, we do not have a specific "message" for each capture
        if captured_header[0] == -1 and captured_header[1] is not None:
            captured_header = (first_row, captured_header[1])
        # Format captured header
        header_str = str(captured_header[1]) if captured_header[1] is not None else "<Undefined>"
        header_str = header_str.replace("{count}", str(len(captured_data))).strip()
        captured_header = (captured_header[0], header_str)
        # Drop all captured rows from data and metadata except the header
        drop_indices = [idx for idx in captured_data.index if idx != captured_header[0]]
        self.data = self.data.loc[~self.data.index.isin(drop_indices)]
        self.metadata = self.metadata.loc[~self.metadata.index.isin(drop_indices)]
        # Merge generated metadata with existing metadata
        # TODO: Figure out a different way to merge metadata, this is too strict
        self.metadata.at[captured_header[0]] = merge_dicts(self.metadata.at[captured_header[0]],
        {
            RMetaNS.General.name: {
                RMetaNS.General.ForegroundColor: "#878787",
                RMetaNS.General.BackgroundColor: "#FFFFFF",
            },
            RMetaNS.CaptureRows.name: {
                RMetaNS.CaptureRows.CaptureRows: captured_header[1],
                RMetaNS.CaptureRows.FromToIndexes: (first_row, last_row),
                RMetaNS.CaptureRows.CollapsedInTotal: len(captured_data)
            }
        })
        # Add new row to data with captured header
        self.data.at[captured_header[0], RColNameNS.Message] = captured_header[1]
        # Sort by index to maintain order
        self.data.sort_index(inplace=True)
        self.metadata.sort_index(inplace=True)
        # print(f"After capture, data is:\n{self.data}\nWith metadata:\n{self.metadata}\n")

    def set_collapsable(self, collapsable:Series, replace:str=None):
        ''' Set or update the collapsable Series.'''
        class CapturedData:
            def __init__(self):
                self.header_idx = -1
                self.header_fmt = None
                self.begin_idx = -1
                self.end_idx = -1

            def reset(self):
                self.header_idx = -1
                self.header_fmt = None
                self.begin_idx = -1
                self.end_idx = -1
        
        captured_data = CapturedData()
        if len(self.data[RColNameNS.Message]) != len(collapsable):
            raise ValueError("collapsable Series must have the same length as the data Message column.")
        for row_idx in self.data.index:
            orig_message = self.data.at[row_idx, RColNameNS.Message]
            new_message = collapsable.at[row_idx]
            # No changes, see if we captured anything
            if orig_message == new_message:
                # We did capture something, save it
                if captured_data.begin_idx != -1 and captured_data.end_idx != -1:
                    self.__capture(
                        (captured_data.header_idx, captured_data.header_fmt if captured_data.header_fmt is not None else replace),
                        self.data.loc[captured_data.begin_idx:captured_data.end_idx].copy(),
                    )
                    # Reset captured data and metadata
                    captured_data.reset()
            
            # Modified message indicates start of capture group
            elif new_message != None:
                # Save new message as a header for Message column
                captured_data.header_idx, captured_data.header_fmt = row_idx, new_message
                # Capture data and metadata
                captured_data.begin_idx, captured_data.end_idx = row_idx if captured_data.begin_idx == -1 else captured_data.begin_idx, row_idx

            # None is the continuation of a capture
            # If replace is defined, it can also be the start of a capture group
            elif new_message == None:
                # Capture data and metadata
                captured_data.begin_idx, captured_data.end_idx = row_idx if captured_data.begin_idx == -1 else captured_data.begin_idx, row_idx
        # Capture very end if any is left
        if captured_data.begin_idx != -1 and captured_data.end_idx != -1:
            self.__capture(
                (captured_data.header_idx, captured_data.header_fmt if captured_data.header_fmt is not None else replace),
                self.data.loc[captured_data.begin_idx:captured_data.end_idx].copy(),
            )
        return self
