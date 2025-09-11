from processor.processor_intf import IProcessor, MetadataColumn

from pandas import DataFrame

from util.config_store import ConfigManager as CfgMan, ConfigStore, Config
from util.presets_manager import PresetsManager

class ColorLogsProcessor(IProcessor):
    def register_config_store(self) -> ConfigStore|Config|None:
        return ConfigStore("color_logs",
                Config("color_logs_enabled", True, type_of=bool),
                Config("color_scheme", [], type_of=list, element_type=str),
                presetsmanager=PresetsManager("color")
            )
    # We expect input to be dataframe type with at least a 'Line' column
    def process(self, data):
        if not isinstance(data, DataFrame):
            raise ValueError("Input must be a pandas DataFrame")
        if data.empty or CfgMan().get(CfgMan().r.color_logs.color_logs_enabled, True) is False:
            print("Color logs process skipped due to empty data or disabled color logs.")
            return None
        
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
        
        return [MetadataColumn(data["Foreground"]), MetadataColumn(data["Background"])]