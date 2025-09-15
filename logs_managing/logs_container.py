from pandas import DataFrame, Series, concat

from util.dict_merge import merge_dicts, overlay_dict

from logs_managing.reserved_names import RESERVED_COLUMN_NAMES as RColNameNS
from logs_managing.reserved_names import RESERVED_METADATA_NAMES as RMetaNS

class LogsContainer():
    ''' Container for both data and all its related properties and details. '''
    def __init__(self):
        self.data = DataFrame()
        self.metadata = Series([], name="METADATA")
        self.collapsed_rows = Series([], name="COLLAPSABLE")
    
    def clear(self):
        self.data = DataFrame()
        self.metadata = Series([], name="METADATA")
        self.collapsed_rows = Series([], name="COLLAPSABLE")
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
            # Replace original column with new one
            self.data = self.data.drop(columns=[name], errors='ignore')
            # Add column to the end
            self.data[name] = column.copy()
        return self
    
    def get_data(self, row:int|list[int]=None) -> DataFrame:
        if row is None:
            return self.data.copy()
        elif isinstance(row, int):
            return self.data.iloc[[row]].copy()
        elif isinstance(row, list):
            return self.data.iloc[row].copy()
        else:
            raise ValueError("Invalid row index type.")





    def set_metadata(self, metadata:Series):
        ''' Set or update the metadata Series. '''
        if self.data.empty:
            raise ValueError("Data must be set before setting metadata.")
        elif len(metadata) != len(self.data):
            raise ValueError("New metadata must have the same number of rows as existing data.")
        elif metadata.dtype != dict:
            raise ValueError("Metadata must be a pandas Series of dictionaries.")
        elif self.metadata.empty:
            self.metadata = metadata.copy()
        else:
            self.metadata = self.metadata.combine(metadata, merge_dicts)
        return self
    
    def get_metadata(self, row:int|list[int]=None) -> Series:
        if row is None:
            return self.metadata.copy()
        elif isinstance(row, int):
            return self.metadata.iloc[[row]].copy()
        elif isinstance(row, list):
            return self.metadata.iloc[row].copy()
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
        style_column = Series(
            {
                RMetaNS.General.name: {
                    RMetaNS.General.ForegroundColor: "#000000",
                    RMetaNS.General.BackgroundColor: "#FFFFFF",
                    RMetaNS.General.FontStyle: "normal",
                }
            }*len(self.data), name="Style"
        )
        style_column = style_column.combine(self.metadata, overlay_dict)
        if row is None:
            return style_column
        elif isinstance(row, int):
            return style_column.iloc[[row]].copy()
        elif isinstance(row, list):
            return style_column.iloc[row].copy()
        else:
            raise ValueError("Invalid row index type.")





    def set_collapsable(self, collapsable:Series, replacement:str|Series):
        ''' Set or update the collapsable Series.'''
        if not isinstance(replacement, str) and not \
            (isinstance(replacement, Series) and replacement.dtype == str and len(replacement) == len(collapsable)):
            raise ValueError("Replacement must be a string or a pandas Series of strings with the same length as collapsable.")
        if self.data.empty:
            raise ValueError("Data must be set before setting collapsable.")
        elif len(collapsable) != len(self.data):
            raise ValueError("New collapsable must have the same number of rows as existing data.")
        elif collapsable.dtype != int:
            raise ValueError(f"Collapsable must be a pandas Series of integers. Current:{collapsable.dtype}")
        elif self.metadata.empty:
            self.metadata = collapsable.copy()
        else:
            captured_uid = 0
            captured_data = DataFrame()
            captured_metadata = Series()
            if replacement is not None:
                for row in range(collapsable.size):
                    current_uid = collapsable.iat[row]
                    # If starting a new capture
                    if current_uid > 0 and captured_uid == 0:
                        captured_uid = current_uid
                        captured_data = concat([captured_data, self.data.iloc[[row]]], copy=True)
                        captured_metadata = concat([captured_metadata, self.metadata.iloc[[row]]], copy=True)
                    # If continuing the current capture
                    elif current_uid == captured_uid and captured_uid != 0:
                        captured_data = concat([captured_data, self.data.iloc[[row]]], copy=True)
                        captured_metadata = concat([captured_metadata, self.metadata.iloc[[row]]], copy=True)
                    # If ending a capture (UID changes or goes to 0)
                    elif captured_uid != 0 and (current_uid != captured_uid or current_uid == 0):
                        # Finalize the captured group
                        if not captured_data.empty and not captured_metadata.empty:
                            if isinstance(replacement, str):
                                message_value = replacement.replace("{count}", str(len(captured_data)))
                            else:
                                message_value = replacement[captured_data.index[0]:captured_data.index[-1]+1].drop_duplicates().values[-1]
                            # Get the first index of the captured data
                            first_index = captured_data.index[0]
                            # Store the captured data and metadata in collapsed_rows
                            self.collapsed_rows[first_index] = (captured_data.copy(), captured_metadata.copy())
                            # Drop data and metadata rows of captured data
                            self.data = self.data.drop(captured_data.index)
                            self.metadata = self.metadata.drop(captured_metadata.index)
                            # Replace values at the first index with the collapse heading
                            self.data.loc[first_index] = [""]*len(self.data.columns)
                            self.metadata.loc[first_index] = dict()
                            # Order properly after dropping and adding rows
                            self.data = self.data.sort_index()
                            self.metadata = self.metadata.sort_index()
                            # Update data and metadata for collapsing header
                            self.data.at[first_index, RColNameNS.Message] = message_value
                            self.metadata.at[first_index] = {
                                RMetaNS.CollapsedRows.name: {
                                    RMetaNS.CollapsedRows.CollapsedRows: captured_data.copy(),
                                    RMetaNS.CollapsedRows.FromToIndexes: (captured_data.index[0], captured_data.index[-1]),
                                    RMetaNS.CollapsedRows.CollapsedInTotal: len(captured_data)
                                }
                            }
                        # Reset for next capture
                        captured_uid = 0
                        captured_data = DataFrame()
                        captured_metadata = Series()
                        # If new UID is starting, start capturing
                        if current_uid > 0:
                            captured_uid = current_uid
                            captured_data = concat([captured_data, self.data.iloc[[row]]], copy=True)
                            captured_metadata = concat([captured_metadata, self.metadata.iloc[[row]]], copy=True)
                # Finalize any remaining capture at the end
                if captured_uid != 0 and not captured_data.empty and not captured_metadata.empty:
                    if isinstance(replacement, str):
                        message_value = replacement.replace("{count}", str(len(captured_data)))
                    else:
                        message_value = replacement[captured_data.index[0]:captured_data.index[-1]+1].drop_duplicates().values[-1]
                    first_index = captured_data.index[0]
                    self.collapsed_rows[first_index] = (captured_data.copy(), captured_metadata.copy())
                    self.data = self.data.drop(captured_data.index)
                    self.metadata = self.metadata.drop(captured_metadata.index)
                    self.data.loc[first_index] = [""]*len(self.data.columns)
                    self.metadata.loc[first_index] = dict()
                    self.data = self.data.sort_index()
                    self.metadata = self.metadata.sort_index()
                    self.data.at[first_index, RColNameNS.Message] = message_value
                    self.metadata.at[first_index] = {
                        RMetaNS.CollapsedRows.name: {
                            RMetaNS.CollapsedRows.CollapsedRows: captured_data.copy(),
                            RMetaNS.CollapsedRows.FromToIndexes: (captured_data.index[0], captured_data.index[-1]),
                            RMetaNS.CollapsedRows.CollapsedInTotal: len(captured_data)
                        }
                    }
            else:
                raise ValueError("Replacement cannot be None. We cannot simply hide rows without a way to indicate they are collapsed.")
        return self
    
    def get_collapsable(self, row:int|list[int]=None) -> Series:
        if row is None:
            return self.collapsed_rows.copy()
        elif isinstance(row, int):
            return self.collapsed_rows.iloc[[row]].copy()
        elif isinstance(row, list):
            return self.collapsed_rows.iloc[row].copy()
        else:
            raise ValueError("Invalid row index type.")
    
