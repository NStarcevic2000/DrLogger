import traceback
import time

from util.singleton import singleton
from logs_managing.logs_manager import LogsManager
from logs_managing.logs_column_types import COLUMN_TYPE
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
            ColorLogsProcessor(),
            FilterLogsProcessor(),
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
                # Perform processing over "non-collapsed" visible data
                # (metadata columns are not visible to processors)
                # Only the first processor gets the list of log files as input
                input_data = LogsManager().get_data(show_collapsed=False) if processor != self.processors[0] else CfgMan().get(CfgMan().r.open_logs.log_files)
                print(f"Input data type: {type(input_data)}")
                print(input_data)
                returned_columns = processor.process(input_data)
                # If the processor returns a generator (yields), collect all yielded columns
                if returned_columns is None:
                    print(f"Processor {processor.__class__.__name__} returned no columns. Skipping...")
                    continue
                elif not isinstance(returned_columns, list) or not all(isinstance(col, COLUMN_TYPE) for col in returned_columns):
                    raise ValueError(f"Processor {processor.__class__.__name__} returned invalid data type: {type(returned_columns)}")
                # Update logs manager with new columns
                print(f"Processor {processor.__class__.__name__} returned {len(returned_columns)} columns.")
                LogsManager().add_new_columns(returned_columns)
            except Exception as e:
                print(f"Error running processor {processor.__class__.__name__}: {e}")
                traceback.print_exc()
            end_time = time.time()
            for col in LogsManager().get_columns():
                print(f"{col.__class__.__name__}({col.name})")
            print(f"Processor {processor.__class__.__name__} finished in {end_time - start_time:.4f} seconds.")
        LogsManager().finalize()
        print("Processing complete.")
        print(LogsManager().get_data())