from typing import Callable
from processor.processorIntf import ProcessorInterface

from pandas import DataFrame, Series

from util.config_store import ConfigManager as CfgMan
from util.config_enums import CONTEXTUALIZE_LINES_ENUM


class FilterLogsProcess(ProcessorInterface):
    def __init__(self, on_start:Callable=None, on_done:Callable=None, on_error:Callable=None):
        
        self.cached_data = DataFrame()
        super().__init__("FilterLogsProcess", on_start, on_done, on_error)

    # We expect input to be dataframe type with at least a 'Line' column
    def process(self, data,
                filter_pattern_arg:list|None=None,
                contextualize_lines_count_arg:int|None=None,
                contextualize_lines_type_arg:CONTEXTUALIZE_LINES_ENUM|None=None,
                keep_hidden_logs_arg:bool|None=None) -> DataFrame:
        if not isinstance(data, DataFrame):
            raise ValueError("Input must be a pandas DataFrame")
        if data.empty:
            self.cached_data = data
            return data
        
        if filter_pattern_arg is not None:
            filter_pattern_data = filter_pattern_arg
        else:
            filter_pattern_data = CfgMan().get(CfgMan().r.filter_logs.filter_pattern, [])
        
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

        if contextualize_lines_count_arg is not None:
            contextualize_lines_count = contextualize_lines_count_arg
        else:
            contextualize_lines_count = CfgMan().get(CfgMan().r.filter_logs.contextualize_lines_count, 0)
        contextualize_lines_count = max(contextualize_lines_count, 0)

        if contextualize_lines_type_arg is not None:
            contextualize_lines_type = contextualize_lines_type_arg.value
        else:
            contextualize_lines_type = CfgMan().get(CfgMan().r.filter_logs.contextualize_lines, CONTEXTUALIZE_LINES_ENUM.NONE.value)
        contextualize_lines_type = CONTEXTUALIZE_LINES_ENUM(contextualize_lines_type)
        
        if contextualize_lines_count > 0:
            # For each line within contextualize_lines distance from a "show" line, set "show" to True
            show_indices = data.index[data["show"]]
            mask = Series(False, index=data.index)
            for idx in show_indices:
                if contextualize_lines_type == CONTEXTUALIZE_LINES_ENUM.LINES_BEFORE:
                    start = max(idx - contextualize_lines_count, data.index[0])
                    end = idx
                elif contextualize_lines_type == CONTEXTUALIZE_LINES_ENUM.LINES_AFTER:
                    start = idx
                    end = min(idx + contextualize_lines_count, data.index[-1])
                elif contextualize_lines_type == CONTEXTUALIZE_LINES_ENUM.LINES_BEFORE_AND_AFTER:
                    start = max(idx - contextualize_lines_count, data.index[0])
                    end = min(idx + contextualize_lines_count, data.index[-1])
                mask.loc[start:end] = True
            data["show"] = mask
        
        # Replace consecutive hidden rows with a single marker row, but do not remove any rows
        hidden_count = 0
        if keep_hidden_logs_arg is not None:
            keep_hidden_logs = keep_hidden_logs_arg
        else:
            keep_hidden_logs = CfgMan().get(CfgMan().r.filter_logs.keep_hidden_logs, False)
        if keep_hidden_logs:
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
