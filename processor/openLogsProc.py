from typing import Callable

from pandas import DataFrame
from enum import Enum

from processor.processorIntf import ProcessorInterface
from util.config_store import ConfigManager as CfgMan, ConfigStore, Config
from util.config_enums import KEEP_SOURCE_FILE_LOCATION_ENUM

class OpenLogsProcess(ProcessorInterface):
    def __init__(self, on_start:Callable=None, on_done:Callable=None, on_error:Callable=None):
        self.cached_data = DataFrame()
        CfgMan().register(
            ConfigStore("open_logs",
                Config("log_files", [], type_of=list, element_type=str),
                Config("keep_source_file_location", KEEP_SOURCE_FILE_LOCATION_ENUM, type_of=Enum),
            ),
        )
        super().__init__("OpenLogsProcess", on_start, on_done, on_error)

    # We expect input to represent log file paths
    def process(self,
                data: str | list | DataFrame | None = None,
                keep_source_file_location_arg:KEEP_SOURCE_FILE_LOCATION_ENUM|None=None) -> DataFrame:
        file_paths = []
        if data is None:
            data = list(CfgMan().get(CfgMan().r.open_logs.log_files, []))
        if isinstance(data, str):
            file_paths.append(data)
        elif isinstance(data, list):
            file_paths.extend(data)
        elif isinstance(data, DataFrame):
            file_paths.extend(data['file_path'].tolist())
        
        print(f"File paths to process: {data}")

        if keep_source_file_location_arg is not None:
            keepSourceFileLocation = keep_source_file_location_arg
        else:
            keepSourceFileLocation = CfgMan().get(CfgMan().r.open_logs.keep_source_file_location, KEEP_SOURCE_FILE_LOCATION_ENUM.NONE.value)
        common_prefix = None
        rows = []

        if keepSourceFileLocation == KEEP_SOURCE_FILE_LOCATION_ENUM.SHORT_PATH: # Short Path
            if len(file_paths) > 1:
                # Find all common string beginnings for all files in file_paths
                common_prefix = min(file_paths, key=len)
            else:
                keepSourceFileLocation = KEEP_SOURCE_FILE_LOCATION_ENUM.FILE_ONLY # File only

        for file_path in file_paths:
            with open(file_path, 'r', errors='ignore') as file:

                if keepSourceFileLocation == KEEP_SOURCE_FILE_LOCATION_ENUM.NONE.value: # None
                    pass
                elif keepSourceFileLocation == KEEP_SOURCE_FILE_LOCATION_ENUM.FILE_ONLY.value: # File only
                    file_path = file_path.split('/')[-1] # Take the last part only
                elif keepSourceFileLocation == KEEP_SOURCE_FILE_LOCATION_ENUM.SHORT_PATH.value: # Short Path
                    file_path = file_path.split('/')[-1] # Take the last part only #TO BE FIXED!!!
                elif keepSourceFileLocation == KEEP_SOURCE_FILE_LOCATION_ENUM.FULL_PATH.value: # Full Path
                    pass

                for line in file:
                    line = line.rstrip('\n')
                    if keepSourceFileLocation == KEEP_SOURCE_FILE_LOCATION_ENUM.NONE.value: # None
                        rows.append({'Line': line})
                    elif keepSourceFileLocation in [
                        KEEP_SOURCE_FILE_LOCATION_ENUM.FILE_ONLY.value,
                        KEEP_SOURCE_FILE_LOCATION_ENUM.SHORT_PATH.value,
                        KEEP_SOURCE_FILE_LOCATION_ENUM.FULL_PATH.value
                    ]: # File only, Short Path, Full Path
                        rows.append({'File': file_path, 'Line': line})

        if rows:
            self.cached_data = DataFrame(rows).reset_index(drop=True)
        else:
            # Ensure DataFrame has correct columns even if no data
            if keepSourceFileLocation:
                self.cached_data = DataFrame(columns=['File', 'Line'])
            else:
                self.cached_data = DataFrame(columns=['Line'])
        return self.cached_data

    def read_cached_data(self):
        return self.cached_data
