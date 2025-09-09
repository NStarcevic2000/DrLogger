from typing import Callable
from processor.processorIntf import ProcessorInterface

from PyQt5.QtWidgets import QTableWidget
from PyQt5.QtGui import QColor

from pandas import DataFrame

from util.config_store import ConfigManager as CfgMan, ConfigStore, Config
from util.presetsManager import PresetsManager

class ColorLogsProcess(ProcessorInterface):
    def __init__(self, on_start:Callable=None, on_done:Callable=None, on_error:Callable=None):
        self.cached_data = DataFrame()
        self.cached_metadata = DataFrame(columns=["Foreground", "Background"])
        CfgMan().register(
            ConfigStore("color_logs",
                Config("color_logs_enabled", True, type_of=bool),
                Config("color_scheme", [], type_of=list, element_type=str),
                presetsmanager=PresetsManager("color")
            ),
        )
        super().__init__("ColorLogsProcess", on_start, on_done, on_error)

    # We expect input to be dataframe type with at least a 'Line' column
    def process(self, data):
        if not isinstance(data, DataFrame):
            raise ValueError("Input must be a pandas DataFrame")
        if data.empty or CfgMan().get(CfgMan().r.color_logs.color_logs_enabled, True) is False:
            print("Color logs process skipped due to empty data or disabled color logs.")
            self.cached_data = data
            return data
        
        color_scheme = CfgMan().get(CfgMan().r.color_logs.color_scheme, [])
        
        # Initialize columns with default colors
        data["Foreground"] = "#000000"
        data["Background"] = "#FFFFFF"
        for column, pattern, foreground, background in color_scheme:
            original_column = column
            if column not in data.columns:
                if "Message" in data.columns:
                    column = "Message"
                elif "Line" in data.columns:
                    column = "Line"
                else:
                    raise ValueError(f"Column '{original_column}' not found in DataFrame, cannot apply color scheme.")
            if not pattern:
                continue
            mask = data[column].astype(str).str.contains(pattern, regex=True, na=False)
            if foreground:
                data.loc[mask, "Foreground"] = foreground
            if background:
                data.loc[mask, "Background"] = background

        self.cached_metadata = data[["Foreground", "Background"]]
        self.cached_data = data.drop(columns=["Foreground", "Background"], errors='ignore')
        print(self.get_metadata())
        return self.cached_data

    def get_metadata(self):
        if not hasattr(self, 'cached_metadata'):
            return DataFrame(columns=["Foreground", "Background"])
        return self.cached_metadata