import unittest

from enum import Enum

from util.config_store import ConfigStore, Config

class SampleEnum(Enum):
    VALUE1 = "value1"
    VALUE2 = "value2"
    VALUE3 = "value3"
    def get_values(): return [e.value for e in SampleEnum]


class TestConfigStore(unittest.TestCase):
    def setUp(self):
        self.cs = ConfigStore("test_store",
            Config("sampleBoolConfig", True, type_of=bool),
            Config("sampleIntConfig", 100, type_of=int),
            Config("sampleEnumConfig", SampleEnum, type_of=Enum),
            Config("sampleListConfig", ["item1", "item2"], type_of=list, element_type=str),
            ConfigStore("sampleNestedConfigStore",
                Config("sampleNestedConfig", "", type_of=str),
            )
        )

    def test_initialization(self):
        self.assertEqual(self.cs.name, "test_store")

    def test_get(self):
        # Test retrieving existing keys
        self.assertTrue(self.cs.get(self.cs.r.sampleBoolConfig, None))
        self.assertEqual(self.cs.get(self.cs.r.sampleEnumConfig, None), SampleEnum.VALUE1.value)

        # Test retrieving non-existent keys
        with self.assertRaises(KeyError):
            self.cs.get("non.existent.key", None)
        with self.assertRaises(KeyError):
            self.cs.get("non.existent.key", "default_value")

    def test_set(self):
        # Test setting existing keys
        self.cs.set(self.cs.r.sampleBoolConfig, False)
        self.assertFalse(self.cs.get(self.cs.r.sampleBoolConfig, None))

    def test_nested_get(self):
        # Test retrieving nested keys
        self.assertEqual(self.cs.get(self.cs.r.sampleNestedConfigStore.sampleNestedConfig, None), "")

    def test_nested_set(self):
        # Test setting nested keys
        self.cs.set(self.cs.r.sampleNestedConfigStore.sampleNestedConfig, "new_value")
        self.assertEqual(self.cs.get(self.cs.r.sampleNestedConfigStore.sampleNestedConfig, None), "new_value")

    def test_overlay_dict(self):
        # Test overlaying a dictionary onto the ConfigStore
        overlay_data = {
            "sampleBoolConfig": True,
            "sampleIntConfig": 10,
            "sampleEnumConfig": "value2",
            "sampleListConfig": ["new_item1", "new_item2"],
            "sampleNestedConfigStore": {
                "sampleNestedConfig": "nested_value"
            },
            "newConfig": "should_not_be_added"
        }
        self.cs.overlay_dict(overlay_data, keep_new_fields=False)
        self.assertTrue(self.cs.get(self.cs.r.sampleBoolConfig, None))
        self.assertEqual(self.cs.get(self.cs.r.sampleIntConfig, None), 10)
        self.assertEqual(self.cs.get(self.cs.r.sampleEnumConfig, None), SampleEnum.VALUE2.value)
        self.assertEqual(self.cs.get(self.cs.r.sampleListConfig, None), ["new_item1", "new_item2"])
        self.assertEqual(self.cs.get(self.cs.r.sampleNestedConfigStore.sampleNestedConfig, None), "nested_value")
        with self.assertRaises(KeyError):
            self.cs.get("newConfig", None)  # Should not be added

    def test_passing_down_config_store(self):
        class SampleProcessorClass:
            def __init__(self, config_store: ConfigStore):
                self.cs = config_store

            def get_config(self, key, default=None):
                return self.cs.get(key, default)
        sample_processor = SampleProcessorClass(self.cs)
        self.cs.set(self.cs.r.sampleBoolConfig, True)
        self.assertTrue(sample_processor.get_config(self.cs.r.sampleBoolConfig, None))
        self.assertEqual(self.cs, sample_processor.cs)
        self.cs.set(self.cs.r.sampleBoolConfig, False)
        self.assertFalse(sample_processor.get_config(self.cs.r.sampleBoolConfig, None))
        self.assertEqual(self.cs, sample_processor.cs)

    def test_invalid_set(self):
        # Test setting invalid types
        with self.assertRaises(ValueError):
            self.cs.set(self.cs.r.sampleIntConfig, "not an int")

    def test_repr(self):
        # Test __repr__ method of Config
        config = self.cs.get(self.cs.r.sampleBoolConfig, None)
        self.assertEqual(repr(config), "True")


# Run this command to start unittest
# python -m unittest discover -s test