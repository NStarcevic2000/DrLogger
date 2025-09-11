import unittest

import os
import tempfile

from util.file_storage_manager import FileStorageManager

class TestFileStorageManager(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.filename = "test_file"
        self.manager = FileStorageManager(dir=self.temp_dir, filename=self.filename)

    def tearDown(self):
        # Remove the directory
        if os.path.exists(self.temp_dir):
            for f in os.listdir(self.temp_dir):
                os.remove(os.path.join(self.temp_dir, f))
            os.rmdir(self.temp_dir)

    def test_init_cache_dir(self):
        cache_dir = self.manager.init_cache_dir()
        self.assertTrue(os.path.exists(cache_dir))

    def test_get_cache_dir(self):
        self.assertEqual(self.manager.get_cache_dir(), self.manager.dir)

    def test_write_to_file_dict(self):
        data = {"key": "value"}
        self.manager.write_to_file(data)
        file_path = os.path.join(self.manager.dir, self.filename + ".json")
        self.assertTrue(os.path.exists(file_path))
        with open(file_path, "r") as f:
            import json
            self.assertEqual(json.load(f), data)

    def test_read_from_file_json(self):
        data = {"key": "value"}
        file_path = os.path.join(self.manager.dir, self.manager.filename)
        with open(file_path, "w") as f:
            import json
            json.dump(data, f)
        self.assertEqual(self.manager.read_from_file(), data)

    def test_delete_file(self):
        file_path = os.path.join(self.manager.dir, self.manager.filename)
        with open(file_path, "w") as f:
            f.write("Test")
        self.assertTrue(os.path.exists(file_path))
        self.manager.delete_file()
        self.assertFalse(os.path.exists(file_path))

# Run this command to start unittest
# python -m unittest discover -s test