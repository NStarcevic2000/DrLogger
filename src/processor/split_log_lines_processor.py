from typing import Callable


from pandas import DataFrame
import re

from processor.processor_intf import IProcessor
from logs_managing.logs_column_types import COLUMN_TYPE, DataColumn
from logs_managing.reserved_names import RESERVED_COLUMN_NAMES as RColNameNS
from util.config_store import ConfigManager as CfgMan, ConfigStore, Config
from util.presets_manager import PresetsManager

class SplitLogLinesProcessor(IProcessor):
    def register_config_store(self) -> ConfigStore|Config|None:
        return ConfigStore("process_logs",
                Config("input_pattern", "", type_of=str),
                Config("timestamp_format", "", type_of=str),
                presetsmanager=PresetsManager("process")
            )

    def process(self, data,
                pattern_format_arg:str|None=None,
                timestamp_format_arg:str|None=None) -> list[COLUMN_TYPE]|None:
        if not isinstance(data, DataFrame):
            raise ValueError("Input must be a pandas DataFrame")
        if RColNameNS.Message not in data.columns and not data.empty:
            raise ValueError(f"DataFrame must contain a {RColNameNS.Message} column (non-empty)")

        # Input:
        # Sample 1 abc:Message 1 cba
        # Sample 2 def:Message 2 fed
        # Sample 3 ghi:Message 3 ihg
        # Pattern: <Group1> <Group2> <Group3>:<Message>
        # Extracted:
        # Group1: Sample, Sample, Sample
        # Group2: 1, 2, 3
        # Group3: abc, def, ghi
        # Message: Message 1 cba, Message 2 fed, Message 3 ihg
        if pattern_format_arg is not None:
            pattern = pattern_format_arg.strip()
        else:
            pattern = CfgMan().get(CfgMan().r.process_logs.input_pattern, "").strip()
        if not pattern:
            return None
        # Replace <Group> with named group that matches any regex word (all but separators)
        regex_pattern = re.sub(r'<(.+?)>', r'(?P<\1>\\w+)', pattern)
        # Replace spaces with \s+ to match any whitespace
        regex_pattern = re.sub(r' ', r'\\s+', regex_pattern)
        
        # Apply regex to each Line in the DataFrame
        try:
            extracted = data[RColNameNS.Message].str.extract(regex_pattern, expand=True)
            for group in re.findall(r'<(.+?)>', pattern):
                if group in extracted.columns:
                    data[group] = extracted[group]
                else:
                    data[group] = None
        except Exception as e:
            print("Error extracting groups:", e)
            return None

        # Convert all possible nan's to empty string
        data = data.fillna("")

        if timestamp_format_arg is not None:
            timestamp_format_arg = timestamp_format_arg.strip()
        else:
            timestamp_format_arg = CfgMan().get(CfgMan().r.process_logs.timestamp_format, "").strip()
        timestamp_tags = re.findall(r'<(.+?)>', timestamp_format_arg)
        agg_format = re.sub(r'<(.+?)>', r'{}', timestamp_format_arg)
        if timestamp_format_arg:
            if False not in [tag in data.columns for tag in timestamp_tags]:
                # Apply extraction from columns to 'Timestamp' column
                # Insert as column 2
                timestamp_col = data[timestamp_tags].apply(
                    lambda row: agg_format.format(*row.values) if all(isinstance(val, str) and val!="" for val in row.values) else "",
                    axis=1
                )
                data.insert(len(timestamp_tags)+1, 'Timestamp', timestamp_col)
                data.drop(columns=timestamp_tags, inplace=True, errors='ignore')

        # Remove matched part (including separators) from RColNameNS.Message to get only the remaining message
        last_group_match = list(re.finditer(r'<(.+?)>', pattern))
        if last_group_match:
            remove_regex = (
            re.sub(r'<(.+?)>', r'\\w+', pattern)
            .replace(' ', r'\s+')
            )
            data[RColNameNS.Message] = data[RColNameNS.Message].str.replace(f'^{remove_regex}', '', regex=True).str.lstrip()
        else:
            data[RColNameNS.Message] = data[RColNameNS.Message]
        # Return new columns first, then the remaining message column
        results = []
        for col in data.columns:
            if col != RColNameNS.Message:
                results.append(DataColumn(data[col]))
        results.append(DataColumn(data[RColNameNS.Message]))
        return results
