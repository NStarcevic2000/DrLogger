from processor.processor_intf import ANY_COLUMN_TYPE, IProcessor, DEFAULT_MESSAGE_COLUMN, DataColumn, CollapsingRowsColumn

from pandas import DataFrame, Series
from enum import Enum

from util.config_store import ConfigManager as CfgMan, ConfigStore, Config
from util.config_enums import CONTEXTUALIZE_LINES_ENUM
from util.presetsManager import PresetsManager


class FilterLogsProcessor(IProcessor):
    def register_config_store(self) -> ConfigStore|Config|None:
        return ConfigStore("filter_logs",
                Config("filter_enabled", True, type_of=bool),
                Config("filter_pattern", [], type_of=list, element_type=str),
                Config("contextualize_lines", CONTEXTUALIZE_LINES_ENUM, type_of=Enum),
                Config("contextualize_lines_count", 5, type_of=int),
                Config("keep_hidden_logs", True, type_of=bool),
                presetsmanager=PresetsManager("filter")
            )
    
    # We expect input to be dataframe type with at least a 'Line' column
    def process(self, data,
                filter_pattern_arg:list|None=None,
                contextualize_lines_count_arg:int|None=None,
                contextualize_lines_type_arg:CONTEXTUALIZE_LINES_ENUM|None=None,
                keep_hidden_logs_arg:bool|None=None) -> list[ANY_COLUMN_TYPE]|None:
        if not isinstance(data, DataFrame):
            raise ValueError("Input must be a pandas DataFrame")
        if data.empty or DEFAULT_MESSAGE_COLUMN not in data.columns:
            return None
        
        if filter_pattern_arg is not None:
            filter_pattern_data = filter_pattern_arg
        else:
            filter_pattern_data = CfgMan().get(CfgMan().r.filter_logs.filter_pattern, [])
        
        if not isinstance(filter_pattern_data, list):
            return None
        if len(filter_pattern_data) == 0:
            return None
        
        data["show"] = False
        # In case the list cannot be parsed correctly, make sure we don't fail completely
        try:
            for pattern_data_pair in filter_pattern_data:
                pattern_column, pattern = pattern_data_pair
                if pattern_column == "" and pattern == "":
                    continue  # Skip empty patterns
                if pattern_column == "":
                    pattern_column = DEFAULT_MESSAGE_COLUMN
                if pattern_column not in data.columns:
                    print(f"Column '{pattern_column}' not found in DataFrame, skipping this pattern.")
                    continue
                data["show"] |= data[pattern_column].astype(str).str.contains(pattern.strip(), regex=True, na=False)
        except Exception as e:
            print("Error applying filter patterns:", e)
            return None

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
        
        # For each line within contextualize_lines distance from a "show" line, set "show" to True
        if contextualize_lines_count > 0 and contextualize_lines_type != CONTEXTUALIZE_LINES_ENUM.NONE:
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
        
        if keep_hidden_logs_arg is None:
            keep_hidden_logs = CfgMan().get(CfgMan().r.filter_logs.keep_hidden_logs, True)
        else:
            keep_hidden_logs = keep_hidden_logs_arg

        if keep_hidden_logs:
            return [CollapsingRowsColumn(data["show"]).set_heading_pattern("< Filtered {count} row(s)>")]
        else:
            return [CollapsingRowsColumn(data["show"])]
