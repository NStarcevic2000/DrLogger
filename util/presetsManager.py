from util.fileStorageManager import FileStorageManager


class PresetsManager(FileStorageManager):
    def __init__(self, name: str):
        super().__init__(dir="presets", filename=name)
        self.presets = {}
        self.presets_location = self.get_cache_dir()
        self.load_presets()

    def load_presets(self):
        ret = self.read_from_file()
        if ret:
            self.presets = ret

    def save_preset(self, name, config_dict):
        self.presets[name] = config_dict
        self.write_to_file(self.presets)

    def get_preset(self, name):
        return self.presets[name] if name in self.presets else None

    def get_all_presets(self):
        return self.presets

    def delete_preset(self, name):
        if name in self.presets:
            del self.presets[name]
            self.write_to_file(self.presets)

    def list_presets(self):
        return list(self.presets.keys())