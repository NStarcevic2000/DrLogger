from pandas import DataFrame

from processor.processor_intf import IProcessor
from logs_managing.logs_column_types import MetadataColumn, PREDEFINED_COLUMN_NAMES as PCN
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
    def process(self, data,
                color_scheme_arg:list|None=None) -> list[MetadataColumn]|None:
        if not isinstance(data, DataFrame) or data.empty:
            return None
        if PCN.MESSAGE.value not in data.columns:
            return None
        
        if color_scheme_arg is not None:
            color_scheme = color_scheme_arg
        else:
            color_scheme = CfgMan().get(CfgMan().r.color_logs.color_scheme, [])

        # Initialize columns with default colors
        data[PCN.FOREGROUND.value] = "#000000"
        data[PCN.BACKGROUND.value] = "#FFFFFF"
        for entry in color_scheme:
            if not isinstance(entry, list):
                continue  # skip invalid color scheme entries
            elif len(entry) != 4:
                continue  # skip invalid color scheme entries
            column, pattern, foreground, background = entry
            data["mask"] = False
            if column == "":
                for col in data.columns:
                    data["mask"] |= data[col].astype(str).str.contains(pattern, regex=True, na=False)
            # If rule applies to a specific column
            elif column in data.columns:
                data["mask"] |= data[column].astype(str).str.contains(pattern, regex=True, na=False)
            else:
                continue
            if foreground:
                data.loc[data["mask"], PCN.FOREGROUND.value] = foreground
            if background:
                data.loc[data["mask"], PCN.BACKGROUND.value] = background
        return [MetadataColumn(data[PCN.FOREGROUND.value]), MetadataColumn(data[PCN.BACKGROUND.value])]