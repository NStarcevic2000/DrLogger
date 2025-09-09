import traceback
import time

from util.singleton import singleton
from util.logs_manager import LogsManager
from util.config_store import ConfigManager as CfgMan
from processor.processor_intf import IProcessor
from processor.open_logs_processor import OpenLogsProcessor
from processor.split_log_lines_processor import SplitLogLinesProcessor
from processor.filter_logs_processor import FilterLogsProcessor
from processor.color_logs_processor import ColorLogsProcessor

@singleton
class ProcessorManager:
    def __init__(self):
        self.processors = [
            OpenLogsProcessor(),
            SplitLogLinesProcessor(),
            FilterLogsProcessor(),
            ColorLogsProcessor(),
        ]

        for processor in self.processors:
            self.initialize_processor(processor)
    
    def get_processors(self) -> list[IProcessor]:
        return self.processors

    def initialize_processor(self, processor: IProcessor):
        CfgMan().register(processor.register_config_store())

    def run(self):
        LogsManager().erase_data()
        for processor in self.get_processors():
            print(f"Running processor: {processor.__class__.__name__}")
            start_time = time.time()
            try:
                input_data = LogsManager().get_visible_data() if processor != self.processors[0] else CfgMan().get(CfgMan().r.open_logs.log_files)
                returned_columns = processor.process(input_data)
                if returned_columns is not None:
                    LogsManager().update_data(returned_columns)
            except Exception as e:
                print(f"Error running processor {processor.__class__.__name__}: {e}")
                traceback.print_exc()
            end_time = time.time()
            print(f"Processor {processor.__class__.__name__} finished in {end_time - start_time:.4f} seconds.")
        print("Processing complete.")