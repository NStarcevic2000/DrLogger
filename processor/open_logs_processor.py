import os
from typing import Callable

from pandas import DataFrame
from enum import Enum

from processor.processor_intf import IProcessor
from util.logs_column import COLUMN_TYPE, DataColumn, MetadataColumn, PREDEFINED_COLUMN_NAMES
from util.config_store import ConfigManager as CfgMan, ConfigStore, Config
from util.config_enums import KEEP_SOURCE_FILE_LOCATION_ENUM

class OpenLogsProcessor(IProcessor):
    def register_config_store(self) -> ConfigStore|Config|None:
        return ConfigStore("open_logs",
            Config("log_files", [], type_of=list, element_type=str),
            Config("keep_source_file_location", KEEP_SOURCE_FILE_LOCATION_ENUM, type_of=Enum),
        )
    
    
    # We expect input to represent log file paths
    def process(self,
                data: str | list | DataFrame | None = None,
                keep_source_file_location_arg:KEEP_SOURCE_FILE_LOCATION_ENUM|None=None) -> list[COLUMN_TYPE]:
        file_paths = []
        if data is None:
            data = list(CfgMan().get(CfgMan().r.open_logs.log_files, []))
        if isinstance(data, str):
            file_paths.append(data)
        elif isinstance(data, list) and len(data) > 0 and all(isinstance(item, str) for item in data):
            file_paths.extend(data)
        else:
            return None  # No valid files to open

        if keep_source_file_location_arg is not None:
            keepSourceFileLocation = keep_source_file_location_arg.value
        else:
            keepSourceFileLocation = CfgMan().get(CfgMan().r.open_logs.keep_source_file_location, KEEP_SOURCE_FILE_LOCATION_ENUM.NONE.value)
        keepSourceFileLocation = KEEP_SOURCE_FILE_LOCATION_ENUM(keepSourceFileLocation)

        common_path_prefix = ""
        if keepSourceFileLocation == KEEP_SOURCE_FILE_LOCATION_ENUM.NONE: # No prefix to remove
            common_path_prefix = ""
        elif keepSourceFileLocation == KEEP_SOURCE_FILE_LOCATION_ENUM.SHORT_PATH: # Remove common path prefix
            if len(file_paths) == 1:
                common_path_prefix = os.path.dirname(file_paths[0])
            else:
                common_path_prefix = os.path.commonpath(file_paths)
        rows = []
        for file_path in file_paths:
            with open(file_path, 'r', errors='ignore', encoding='utf-8') as file:
                for line in file:
                    # Strip any line ending whitespace/newline characters
                    line = line.rstrip()
                    if keepSourceFileLocation == KEEP_SOURCE_FILE_LOCATION_ENUM.FULL_PATH:
                        visible_file_value = file_path
                    elif keepSourceFileLocation == KEEP_SOURCE_FILE_LOCATION_ENUM.FILE_ONLY:
                        visible_file_value = os.path.basename(file_path)
                    elif keepSourceFileLocation == KEEP_SOURCE_FILE_LOCATION_ENUM.SHORT_PATH:
                        visible_file_value = file_path.replace(common_path_prefix, "", 1).replace("\\", "/").lstrip("/")
                    else:
                        visible_file_value = ""
                    
                    rows.append({
                        PREDEFINED_COLUMN_NAMES.FILE.value: visible_file_value,
                        PREDEFINED_COLUMN_NAMES.MESSAGE.value: line,
                        'Original Messages': line
                    })
        data = DataFrame(rows).reset_index(drop=True)
        # Optionally, return the 'File' column if requested
        result = []
        if keepSourceFileLocation != KEEP_SOURCE_FILE_LOCATION_ENUM.NONE:
            result.append(DataColumn(data[PREDEFINED_COLUMN_NAMES.FILE.value]))
        # Always return the 'Message' column
        result.append(DataColumn(data[PREDEFINED_COLUMN_NAMES.MESSAGE.value]))
        # We would like to keep the original messages for displaying them in detail
        result.append(MetadataColumn(data['Original Messages']))
        return result
