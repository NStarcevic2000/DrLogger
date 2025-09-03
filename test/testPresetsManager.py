import json
import os
import tempfile
import unittest
from util.presetsManager import PresetsManager

class TestPresetsManager(unittest.TestCase):
    def setUp(self):
        self.manager = PresetsManager("test_file")

    def tearDown(self):
        # Clean up test directory after each test
        get_current_file_path = self.manager.get_current_file_path()
        if get_current_file_path and os.path.exists(get_current_file_path):
            os.remove(get_current_file_path)
    
    def test_save_preset(self):
        config = {'a': 1, 'b': 2}
        self.manager.save_preset('test1', config)
        loaded = self.manager.get_preset('test1')
        self.assertEqual(loaded, config)
        # Check if the file is created
        self.assertTrue(os.path.exists(self.manager.get_current_file_path()))
        # Check the file content
        with open(self.manager.get_current_file_path(), 'r') as f:
            content = f.read()
            self.assertEqual(json.loads(content), dict({'test1':config}))

    def test_get_nonexistent_preset(self):
        self.assertIsNone(self.manager.get_preset('does_not_exist'))

    def test_delete_preset(self):
        config = {'x': 42}
        self.manager.save_preset('to_delete', config)
        self.assertIsNotNone(self.manager.get_preset('to_delete'))
        self.manager.delete_preset('to_delete')
        self.assertIsNone(self.manager.get_preset('to_delete'))
        self.assertNotIn('to_delete', self.manager.list_presets())

    def test_list_presets(self):
        self.manager.save_preset('one', {'a': 1})
        self.manager.save_preset('two', {'b': 2})
        presets = self.manager.list_presets()
        self.assertIn('one', presets)
        self.assertIn('two', presets)
        self.assertEqual(len(presets), 2)

if __name__ == '__main__':
    unittest.main()