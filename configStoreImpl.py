from enum import Enum

from util.configStore import Config, ConfigStore
from util.fileStorageManager import FileStorageManager
from util.presetsManager import PresetsManager

class KEEP_SOURCE_FILE_LOCATION_ENUM(Enum):
    NONE = "None"
    FILE_ONLY = "File only"
    SHORT_PATH = "Short Path"
    FULL_PATH = "Full Path"
    def get_values(): return [e.value for e in KEEP_SOURCE_FILE_LOCATION_ENUM]

class CONTEXTUALIZE_LINES_ENUM(Enum):
    NONE = "None"
    LINES_BEFORE = "Lines before"
    LINES_AFTER = "Lines after"
    LINES_BEFORE_AND_AFTER = "Lines before and after"
    def get_values(): return [e.value for e in CONTEXTUALIZE_LINES_ENUM]


masterConfigStore = \
ConfigStore("master",
    ConfigStore("preferences",
        Config("autoSave", True, type_of=bool),
        Config("preview_max_lines", 5, type_of=int),
        Config("presets_location_path", "", type_of=str)
    ),
    ConfigStore("open_logs",
        Config("log_files", [], type_of=list, element_type=str),
        Config("keep_source_file_location", KEEP_SOURCE_FILE_LOCATION_ENUM, type_of=Enum),
    ),
    ConfigStore("process_logs",
        Config("input_pattern", "", type_of=str),
        Config("timestamp_format", "", type_of=str),
        presetsmanager=PresetsManager("process")
    ),
    ConfigStore("color_logs",
        Config("color_logs_enabled", True, type_of=bool),
        Config("color_scheme", [], type_of=list, element_type=str),
        presetsmanager=PresetsManager("color")
    ),
    ConfigStore("filter_logs",
        Config("filter_enabled", True, type_of=bool),
        Config("filter_pattern", [], type_of=list, element_type=str),
        Config("contextualize_lines", CONTEXTUALIZE_LINES_ENUM, type_of=Enum),
        Config("contextualize_lines_count", 5, type_of=int),
        Config("keep_hidden_logs", True, type_of=bool),
        presetsmanager=PresetsManager("filter")
    ),
    fsmanager=FileStorageManager(None, "session")
)