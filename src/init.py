# main.py
import cProfile
import sys
from PyQt5.QtWidgets import QApplication

from processor.processor_manager import ProcessorManager
from util.config_manager import ConfigManager as CfgMan, ConfigStore, Config
from logs_managing.logs_manager import LogsManager
from util.presets_manager import PresetsManager
from util.config_enums import (
    KEEP_SOURCE_FILE_LOCATION_ENUM,
    CONTEXTUALIZE_LINES_ENUM
)

from gui.main_window import DrLoggerMainWindow
import pstats

if __name__ == "__main__":
    app = QApplication(sys.argv)

    # Initialization purposes
    ProcessorManager()

    viewer = DrLoggerMainWindow()
    viewer.show()
    viewer.editor_prompt.show()
    # Benchmark performance of initial rendering
    # profiler = cProfile.Profile()
    # profiler.enable()
    # viewer.update()
    # profiler.disable()
    # stats = pstats.Stats(profiler).sort_stats('cumtime').print_callees('__capture')
            

    sys.exit(app.exec_())