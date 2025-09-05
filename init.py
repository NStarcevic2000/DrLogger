# main.py
import sys
from PyQt5.QtWidgets import QApplication

from util.config_store import ConfigManager as CfgMan, ConfigStore, Config
from util.presetsManager import PresetsManager
from util.config_enums import (
    KEEP_SOURCE_FILE_LOCATION_ENUM,
    CONTEXTUALIZE_LINES_ENUM
)

from enum import Enum

from processor.processPipeline import ProcessPipeline

from gui.mainWindow import DrLogMainWindow

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    masterConfigStore = CfgMan().register(
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
    )

    viewer = DrLogMainWindow()
    viewer.show()

    sys.exit(app.exec_())