from typing import Callable
from processor.processorIntf import ProcessorInterface

from pandas import DataFrame, Series

from util.configStore import ConfigStore


class FilterLogsProcess(ProcessorInterface):
    def __init__(self, configStore:ConfigStore, on_start:Callable=None, on_done:Callable=None, on_error:Callable=None):
        self.cs = configStore
        self.cached_data = DataFrame()
        super().__init__("FilterLogsProcess", on_start, on_done, on_error)

    # We expect input to be dataframe type with at least a 'Line' column
    def process(self, data):
        if not isinstance(data, DataFrame):
            raise ValueError("Input must be a pandas DataFrame")
        if data.empty:
            self.cached_data = data
            return data
        filter_pattern_data = self.cs.get(self.cs.r.filter_logs.filter_pattern, [])
        filter_pattern_data = [(col, pat) for col, pat in filter_pattern_data if (pat.strip() != "" and pat.strip() != "")]
        if not filter_pattern_data or not isinstance(filter_pattern_data, list):
            print("No filter patterns provided, skipping filter logs process.")
            self.cached_data = data
            return data
        data["show"] = False
        for pattern_column, pattern in filter_pattern_data:
            if pattern_column == "" and pattern == "":
                continue  # Skip empty patterns
            if pattern_column == "":
                pattern_column = "Message"
            if pattern_column not in data.columns:
                print(f"Column '{pattern_column}' not found in DataFrame, skipping this pattern.")
                continue
            data["show"] |= data[pattern_column].astype(str).str.contains(pattern.strip(), regex=True, na=False)

        contextualize_lines = max(self.cs.get(self.cs.r.filter_logs.contextualize_lines_count, 0), 0)
        if contextualize_lines > 0:
            # For each line within contextualize_lines distance from a "show" line, set "show" to True
            show_indices = data.index[data["show"]]
            mask = Series(False, index=data.index)
            for idx in show_indices:
                start = max(idx - contextualize_lines, data.index[0])
                end = min(idx + contextualize_lines, data.index[-1])
                mask[start:end+1] = True
            data["show"] = mask
        
        # Replace consecutive hidden rows with a single marker row, but do not remove any rows
        hidden_count = 0
        if self.cs.get(self.cs.r.filter_logs.keep_hidden_logs, False):
            for i in range(len(data)):
                if not data.iloc[i]["show"]:
                    hidden_count += 1
                    # If next row is shown or end of data, mark this row
                    if i + 1 == len(data) or data.iloc[i + 1]["show"]:
                        data.at[i, "show"] = True
                        # All other columns should be set to empty
                        for col in data.columns:
                            if col != "show":
                                data.at[i, col] = ""
                        row_word = "row" if hidden_count == 1 else "rows"
                        data.at[i, "Message"] = f"< filtered {hidden_count} {row_word} >"
                        hidden_count = 0
                else:
                    hidden_count = 0
        self.cached_data = data[data["show"]].drop(columns=["show"], errors='ignore')
        return self.cached_data
