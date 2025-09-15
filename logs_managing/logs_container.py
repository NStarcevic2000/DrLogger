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
        ''' Set or update the main data DataFrame. '''
        if not isinstance(column, Series) or column.dtype != "string":
            raise ValueError("column must be a pandas Series of strings.")
        elif self.data.empty:
            self.data = DataFrame(column, columns=[name]).copy()
        elif len(column) != len(self.data):
            raise ValueError("New data must have the same number of rows as existing data.")
        else:
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
            # If there is a collapse pattern, insert a heading row for each group of collapsed rows
            captured_data = DataFrame()
            captured_metadata = DataFrame()
            if replacement is not None:
                for row in range(collapsable.size):
                    # Found collapsable UID
                    if collapsable.iat[row] > 0:
                        captured_data = concat([captured_data, self.data.iloc[row:row+collapsable.iat[row]]])
                        captured_metadata = concat([captured_metadata, self.metadata.iloc[row:row+collapsable.iat[row]]])
                        continue
                    # If it is not a collapsable UID, see if we have captured some data to insert a heading row
                    elif not captured_data.empty or not captured_metadata.empty:
                        collapsable_chunk_metadata = {
                            "Collapsed Rows": {
                                "Collapsed Rows": captured_data,
                                "From-To Indexes": (captured_data.index[0], captured_data.index[-1]),
                                "Collapsed in Total": len(captured_data),
                            }
                        }
                        # Clear captured data from self.data
                        self.data = self.data.drop(captured_data.index)
                        # Insert heading row in the index of the first captured element
                        # If replacement is a string, use it with {count} replaced by the number of collapsed rows
                        # If replacement is a Series, use the last string set within the captured rows
                        self.data.insert(captured_data.index[0], RColNameNS.Message,
                            replacement.replace("{count}", str(len(captured_data))) if isinstance(replacement, str) else \
                            replacement[captured_data.index[0]:captured_data.index[-1]].values.unique()[-1]
                        )
                        # Clear captured metadata from self.metadata
                        self.metadata = self.metadata.drop(captured_metadata.index)
                        # Replace metadata with collapsable metadata
                        self.metadata.at[captured_metadata.index[0]] = collapsable_chunk_metadata
                        # Save captured data and metadata
                        self.collapsed_rows[captured_data.index[0]] = (captured_data, captured_metadata)
                        # Clear captured data and metadata
                        captured_data = DataFrame()
                        captured_metadata = DataFrame()
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
    
