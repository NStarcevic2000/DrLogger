from collections.abc import Callable
from types import SimpleNamespace
from enum import Enum

from util.singleton import singleton
from util.file_storage_manager import FileStorageManager
from util.presets_manager import PresetsManager



class Config(dict):
    def __init__(self, name: str, value, type_of: type,
                 element_type: type = None, on_warning: Callable = None):
        super().__init__()
        self.name = name
        self.value = value
        if self.value is None:
            raise ValueError(f"Value for {name} cannot be None on initialization.")
        self.default = value
        self.possible_values = None
        self.type = type_of
        if self.type in [list, dict]:
            if element_type is None:
                raise ValueError(f"element_type must be provided for type {self.type} in Config {name}.")
            else:
                self.element_type = element_type
        self.element_type = element_type
        self.on_warning = on_warning

        if self.type == bool:
            self.possible_values = [True, False]
        elif self.type == Enum:
            self.possible_values = self.value.get_values()
            self.value = self.possible_values[0]

    def get(self, default=None):
        return self.value if self.value is not None else default

    def set(self, value):
        print(f"Setting {self.name} to {value}")
        if self.possible_values:
            if value not in self.possible_values:
                self.raise_warning(f"Value {value} is not in possible values for {self.name}. Possible values are: {self.possible_values}")
            else:
                self.value = value
        elif isinstance(value, self.type):
            self.value = value
        else:
            self.raise_warning(f"Value {value} is not of type {self.type} for {self.name}.")
        return self

    def reset(self):
        self.value = self.default

    def __repr__(self):
        return {
            "name": self.name,
            "possible_values": self.possible_values if self.possible_values else None,
        }
    
    def raise_warning(self, message):
        if self.on_warning:
            self.on_warning(message)
        else:
            raise ValueError(message)






class ConfigStore(dict):
    def __init__(self, name: str, *args: "ConfigStore | Config",
                 fsmanager: FileStorageManager = None,
                 presetsmanager: PresetsManager = None,
                 on_warning: Callable = None):
        self.name = name
        self.r = SimpleNamespace()
        self.fsmanager = fsmanager
        self.register(*args)
        self.on_warning = on_warning
        self.pm = presetsmanager
    
    def register(self, *args: "ConfigStore | Config"):
        for arg in args:
            if isinstance(arg, ConfigStore) or isinstance(arg, Config):
                if arg.name in self:
                    # raise ValueError(f"ConfigStore or Config with name {arg.name} already exists in {self.name}...")
                    return
                self[arg.name] = arg
            else:
                raise ValueError(f"Value for {arg} must be ConfigStore or Config, got {type(arg)}")
        # Generate namespaces for easy access
        self.r = self.get_namespaces()
        # Load config from file if fsmanager is provided
        if self.fsmanager:
            try:
                loaded_data = self.fsmanager.read_from_file()
                if loaded_data:
                    self.overlay_dict(loaded_data, keep_new_fields=False)
                else:
                    self.fsmanager.write_to_file(self)
            except Exception as e:
                self.fsmanager.write_to_file(self)
        return self

    def get(self, key: str, default=None):
        # Split the key into parts for nested lookup
        keys = key.split(".")
        current = keys[0]
        if current in self:
            if len(keys) == 1:
                if isinstance(self[current], ConfigStore):
                    return self[current]
                elif isinstance(self[current], Config):
                    return self[current].get(default)
                else:
                    return default
            else:
                if isinstance(self[current], ConfigStore):
                    return self[current].get('.'.join(keys[1:]), default)
                else:
                    return default
        else:
            raise KeyError(f"Key '{key}' not found in ConfigStore '{self.name}'")

    def set(self, key: str, value):
        # Split the key into parts for nested setting
        keys = key.split(".")
        current = keys[0]
        if isinstance(self[current], ConfigStore):
            self[current].set('.'.join(keys[1:]), value)
        elif isinstance(self[current], Config):
            self[current].set(value)
        if self.fsmanager:
            self.fsmanager.write_to_file(self)

    def get_serialized(self, other_dict: dict = None) -> dict:
        """Returns a serialized version of the ConfigStore."""
        serialized = {}
        for key, value in self.items() if other_dict is None else other_dict.items():
            if isinstance(value, ConfigStore):
                serialized[key] = value.get_serialized()
            elif isinstance(value, Config):
                serialized[key] = value.value
            else:
                serialized[key] = value
        return serialized

    # Overlay a dictionary onto the current ConfigStore
    # Apply only "right" to "left" merging for keys existing in both dicts
    def overlay_dict(self, data: dict, keep_new_fields: bool = False):
        if not isinstance(data, dict):
            self.raise_warning(f"Data must be a dictionary, got {type(data)}")
            return self
        for key, value in data.items():
            if isinstance(value, dict):
                if key not in self:
                    if keep_new_fields:
                        self[key] = ConfigStore(key, *[Config(k, v, type(v)) if not isinstance(v, dict) else ConfigStore(k, **v) for k, v in value.items()], fsmanager=None)
                elif key in self and isinstance(self[key], ConfigStore):
                    self[key].overlay_dict(value, keep_new_fields=keep_new_fields)
                else:
                    # If self[key] exists but is not a ConfigStore, replace it if allowed
                    if keep_new_fields:
                        self[key] = ConfigStore(key, value)
            else:
                if key not in self:
                    if keep_new_fields:
                        self[key] = Config(key, value, type(value))
                elif key in self and isinstance(self[key], Config):
                    self[key].set(value)
                else:
                    # If self[key] exists but is not a Config, replace it if allowed
                    if keep_new_fields:
                        self[key] = Config(key, value)
    
    def get_namespaces(self):
        def recursive_namespace(store, prefix=""):
            namespace = {}
            for key, value in store.items():
                full_key = f"{prefix}.{key}" if prefix else key
                if isinstance(value, ConfigStore):
                    ns = recursive_namespace(value, full_key)
                    setattr(ns, "name", full_key)
                    namespace[key] = ns
                elif isinstance(value, Config):
                    namespace[key] = full_key
            return SimpleNamespace(**namespace)
        return recursive_namespace(self)
    
    def raise_warning(self, message):
        if self.on_warning:
            self.on_warning(message)
        else:
            raise ValueError(message)
    
    def __repr__(self):
        return f"{self.name}:{{ {list(self.keys())} }}"
        # To be improved

    def load_presets(self):
        if self.pm:
            self.pm.load_presets()

    def save_preset(self, name, data:dict=None):
        if self.pm:
            if data is None:
                data = self.get_serialized()
            self.pm.save_preset(name, data)

    def get_preset(self, name):
        if self.pm:
            return self.pm.get_preset(name)
        return None

    def get_all_presets(self):
        if self.pm:
            return self.pm.get_all_presets()
        return {}

    def delete_preset(self, name):
        if self.pm:
            self.pm.delete_preset(name)
    
    def list_presets(self):
        if self.pm:
            return self.pm.list_presets()
        return []

    def apply_preset(self, name):
        preset_data = self.pm.get_preset(name)
        if preset_data:
            self.overlay_dict(preset_data, keep_new_fields=False)





@singleton
class ConfigManager(ConfigStore):
    def __init__(self):
        super().__init__("ConfigManager",
                         fsmanager=FileStorageManager(None, "session")
        )