from abc import abstractmethod
from typing import Callable, final
import traceback

class ProcessorInterface:
    def __init__(self,
                 name: str,
                 on_start: Callable = None,
                 on_done: Callable = None,
                 on_error: Callable = None):
        self.name = name
        self.on_start = on_start
        self.on_done = on_done
        self.on_error = on_error
        self.next_process = None
    
    @final
    def run(self, data):
        if self.on_start:
            self.on_start(data)
        try:
            data = self.process(data)
            print(f"{self.name} processed data head:\n{data.head()}")
        except Exception as e:
            print(f"Error in {self.name}: {e}")
            traceback.print_exc()
            if self.on_error:
                self.on_error(data)
        if self.on_done:
            self.on_done(data)
        if self.next_process:
            self.next_process.run(data)  # Use run() instead of process() to maintain pipeline
    
    @final
    def attach(self, process: 'ProcessorInterface'):
        self.next_process = process

    @abstractmethod
    def process(self, data):
        pass