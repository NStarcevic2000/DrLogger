from util.config_store import ConfigStore, Config
from util.file_storage_manager import FileStorageManager
from util.singleton import singleton

from util.preferences_enums import *

@singleton
class ConfigManager(ConfigStore):
    def __init__(self):
        super().__init__("ConfigManager",
                         fsmanager=FileStorageManager(None, "session")
        )
    
        # Register preferences as soon as ConfigManager is initialized (these are available globally)
        self.register(
            ConfigStore("preferences",
                ConfigStore("UI",
                    Config("Keep UI Layout", True, type_of=bool),
                    Config("Window Properties", {}, type_of=dict, element_type=str),
                    Config("Theme", PREFERENCES_UI_THEME_ENUM.LIGHT, type_of=PREFERENCES_UI_THEME_ENUM),
                    Config("Font Size", 10, type_of=int),
                    Config("Allow Font Size Change", True, type_of=bool),
                    Config("Font Size Increment", 1, type_of=int),
                ),
                ConfigStore("Auto Functions",
                    Config("Auto Load Last Session", True, type_of=bool),
                    Config("Auto Save Config Changes", True, type_of=bool),
                    Config("Auto Open Previous Log File", True, type_of=bool),
                    Config("Auto Open Editor on Startup", True, type_of=bool),
                ),
                ConfigStore("Exporting Options",
                    Config("Clipboard Delimiter", " ", type_of=str),
                    Config("Export File Delimiter", " ", type_of=str)
                ),
                ConfigStore("Log Rendering",
                    Config("Default Timestamp Format", "YYYY-MM-DD HH:mm:ss.SSS", type_of=str),
                    Config("Keep Corrupted Lines", False, type_of=bool),
                    Config("Max Lines to Preview", 5, type_of=int),
                ),
                # ConfigStore("Warnings",
                #     Config("Show Warnings", True, type_of=bool),
                #     Config("Warn On Large File Open", True, type_of=bool),
                #     Config("Large File Size Threshold (MB)", 50, type_of=int),
                #     Config("Warn On Many Lines", True, type_of=bool),
                #     Config("Many Lines Threshold", 300000, type_of=int),
                #     Config("Warn On Many Columns", True, type_of=bool),
                #     Config("Many Columns Threshold", 10, type_of=int),
                # ),
                ConfigStore("Aliases",
                    Config("Substitutions", {
                        "Info": ["info", "information", "i"],
                        "Error": ["error", "err", "e"],
                        "Warning": ["warning", "warn", "w"],
                        "Debug": ["debug", "d"],
                        "Critical": ["critical", "crit", "c"],
                        "Fatal": ["fatal", "f"],
                        "Year": ["year", "y"],
                        "Month": ["month", "m"],
                        "Day": ["day", "d"],
                        "Hour": ["hour", "h"],
                        "Minute": ["minute", "min", "m"],
                        "Second": ["second", "sec", "s"],
                        "Millisecond": ["millisecond", "ms", "msec"],
                        }, type_of=dict, element_type=list),
                    fsmanager=FileStorageManager(None, "aliases")
                ),
                fsmanager=FileStorageManager(None, "preferences")
            )
        )