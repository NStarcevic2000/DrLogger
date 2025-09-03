import os
import json

class FileStorageManager:
    def __init__(self, dir: str | None, filename: str):
        self.app_name = "DrLog"
        self.dir = self.init_cache_dir(dir)
        self.filename = filename + ".json" if filename else None
    
    def get_current_file_path(self):
        if self.filename is None:
            return None
        return os.path.join(self.dir, self.filename)

    def init_cache_dir(self, dir: str = None) -> str:
        # Create a cache directory if it does not exist
        if dir is None:
            dir = os.path.join(os.path.expanduser("~"), ".cache", self.app_name)
        else:
            dir = os.path.join(os.path.expanduser("~"), ".cache", self.app_name, dir)
        if not os.path.exists(dir):
            os.makedirs(dir, exist_ok=True)
        else:
            print(f"Cache directory already exists: {dir}")
        print(f"Cache directory initialized: {dir}")
        return dir

    def get_cache_dir(self) -> str:
        """Returns the cache directory path."""
        return self.dir
    
    def read_from_file(self) -> dict | None:
        if self.filename is None:
            return None
        file_path = os.path.join(self.dir, self.filename)
        if os.path.exists(file_path):
            with open(file_path, 'r') as f:
                import json
                data = json.load(f)
                print(f"Data read from file: {data}")
                return dict(data)
        return None

    def write_to_file(self, data: dict):
        if self.filename is None:
            raise ValueError("Filename must be set to write to file.")
        file_path = os.path.join(self.dir, self.filename)
        with open(file_path, 'w') as f:
            # Handle plain dict that might contain Config/ConfigStore objects
            serialized_data = self._convert_to_serializable(data)
            json.dump(serialized_data, f, indent=4)
        print(f"Data written to {file_path}: {json.dumps(serialized_data, indent=4)}")

    def _convert_to_serializable(self, obj):
        """Convert ConfigStore/Config objects to serializable dictionaries."""
        if hasattr(obj, 'value') and hasattr(obj, 'name'):  # Config object
            return obj.value
        elif hasattr(obj, 'get_serialized'):  # ConfigStore object
            return obj.get_serialized()
        elif isinstance(obj, dict):
            result = {}
            for key, value in obj.items():
                result[key] = self._convert_to_serializable(value)
            return result
        elif isinstance(obj, (list, tuple)):
            return [self._convert_to_serializable(item) for item in obj]
        else:
            return obj

    def delete_file(self):
        print(f"Deleting file: {os.path.join(self.dir, self.filename)}")
        if self.filename is None:
            raise ValueError("Filename must be set to delete file.")
        file_path = os.path.join(self.dir, self.filename)
        if os.path.exists(file_path):
            os.remove(file_path)
        else:
            print(f"File {file_path} does not exist, nothing to delete.")