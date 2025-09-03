from processor.openLogsProc import OpenLogsProcess
from processor.splitLogLinesProc import SplitLogLinesProcess
from processor.colorLogsProc import ColorLogsProcess
from processor.filterLogsProc import FilterLogsProcess
import hashlib

def md5_checksum(data):
    if data is None:
        return None
    if isinstance(data, str):
        data = data.encode('utf-8')
    return hashlib.md5(data).hexdigest()

class ProcessPipeline:
    def __init__(self, configStore):
        self.cs = configStore

        self.open_logs_process = OpenLogsProcess(self.cs)
        self.split_log_lines_process = SplitLogLinesProcess(self.cs)
        self.filter_logs_process = FilterLogsProcess(self.cs)
        self.color_logs_process = ColorLogsProcess(self.cs)

        self.filter_logs_process.attach(self.color_logs_process)
        self.split_log_lines_process.attach(self.filter_logs_process)
        self.open_logs_process.attach(self.split_log_lines_process)

    def run(self, data=None):
        self.open_logs_process.run(data)
    
    def get_color_metadata(self):
        return self.color_logs_process.cached_metadata

    def get_data(self):
        return self.color_logs_process.cached_data
