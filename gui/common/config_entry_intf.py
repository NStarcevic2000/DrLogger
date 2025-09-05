from abc import ABC, abstractmethod

class IConfigEntry(ABC):
    @abstractmethod
    def update_content(self):
        pass

    @abstractmethod
    def on_config_updated(self):
        pass
