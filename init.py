# main.py
import cProfile
import sys
from PyQt5.QtWidgets import QApplication

from processor.processor_manager import ProcessorManager
from util.config_store import ConfigManager as CfgMan, ConfigStore, Config
from util.presetsManager import PresetsManager
from util.config_enums import (
    KEEP_SOURCE_FILE_LOCATION_ENUM,
    CONTEXTUALIZE_LINES_ENUM
)

from gui.mainWindow import DrLogMainWindow

if __name__ == "__main__":
    app = QApplication(sys.argv)

    # Initialization purposes
    ProcessorManager()
    
    CfgMan().register(
            ConfigStore("preferences",
            Config("autoSave", True, type_of=bool),
            Config("preview_max_lines", 5, type_of=int),
            Config("presets_location_path", "", type_of=str)
        )
    )

    viewer = DrLogMainWindow()
    viewer.show()
    # Benchmark performance of initial rendering
    profiler = cProfile.Profile()
    profiler.enable()
    viewer.update()
    profiler.disable()
    profiler.print_stats(sort='cumtime')

    sys.exit(app.exec_())