import tempfile
import unittest

from util.configStore import ConfigStore, Config
from configStoreImpl import KEEP_SOURCE_FILE_LOCATION_ENUM
from enum import Enum

from pandas import DataFrame
from pandas.testing import assert_frame_equal

from processor.splitLogLinesProc import SplitLogLinesProcess


class TestSplitLogLinesProcess(unittest.TestCase):
    def setUp(self):
        self.cs = ConfigStore("sample_config_store",
            ConfigStore("process_logs",
                Config("input_pattern", "", type_of=str),
                Config("timestamp_format", "", type_of=str),
            )
        )
        self.processor = SplitLogLinesProcess(self.cs)

        # Create a temporary file with sample log data
        self.tmp_file = tempfile.NamedTemporaryFile(delete=False, mode='w+', suffix='.log', encoding='utf-8')
        self.tmp_file.writelines(["Sample 1 abc\n", "Sample 2 def\n", "Sample 3 ghi\n"])
        self.tmp_file.flush()
        self.tmp_file.close()
        super().setUp()

    def tearDown(self):
        import os
        os.unlink(self.tmp_file.name)
        super().tearDown()

    def test_process_valid_dataframe(self):
        # Test processing a valid DataFrame
        self.cs.set(self.cs.r.process_logs.input_pattern, "<Group1> <Group2>:<Group3>")
        input_df = DataFrame({'Line': ["Sample 1:abc", "Sample 2:def", "Sample 3:ghi"]})
        result_df = self.processor.process(input_df)

        expected_df = DataFrame({
            'Group1': ["Sample", "Sample", "Sample"],
            'Group2': ["1", "2", "3"],
            'Group3': ["abc", "def", "ghi"]
        })

        try:
            assert_frame_equal(result_df, expected_df)
        except AssertionError as e:
            print("Result DataFrame:\n", result_df)
            print("Expected DataFrame:\n", expected_df)
            raise

    def test_process_missing_line_column(self):
        # Test processing a DataFrame without 'Line' column
        input_df = DataFrame({'OtherColumn': ["Sample 1 abc", "Sample 2 def", "Sample 3 ghi"]})
        with self.assertRaises(ValueError):
            self.processor.process(input_df)

    def test_empty_dataframe(self):
        # Test processing an empty DataFrame
        input_df = DataFrame({'Line': []})
        self.cs.set(self.cs.r.process_logs.input_pattern, "<Group1> <Group2>:<Group3>")
        self.assertEqual(self.cs.get(self.cs.r.process_logs.input_pattern, 0), "<Group1> <Group2>:<Group3>")
        result_df = self.processor.process(input_df)

        self.assertIsInstance(result_df, DataFrame)
        self.assertEqual(len(result_df), 0)
        assert_frame_equal(result_df, input_df)
    
    def test_timestamp_format(self):
        # Test processing with timestamp format
        self.cs.set(self.cs.r.process_logs.input_pattern, "<Year>-<Month>-<Day> <Hour>:<Minutes>:<Seconds> <Type> <From>:")
        self.cs.set(self.cs.r.process_logs.timestamp_format, "<Year>-<Month>-<Day> <Hour>:<Minutes>:<Seconds>")

        input_df = DataFrame({'Line': ["2023-10-01 12:00:00 Sample 1:abc", "2023-10-01 12:01:00 Sample 2:def", "2023-10-01 12:02:00 Sample 3:ghi"]})
        result_df = self.processor.process(input_df)

        expected_df = DataFrame({
            'Timestamp': ["2023-10-01 12:00:00", "2023-10-01 12:01:00", "2023-10-01 12:02:00"],
            'Type': ["Sample", "Sample", "Sample"],
            'From': ["1", "2", "3"],
            'Message': ["abc", "def", "ghi"]
        })

        try:
            assert_frame_equal(result_df, expected_df)
        except AssertionError as e:
            print("Result DataFrame:\n", result_df)
            print("Expected DataFrame:\n", expected_df)
            raise

# Run this command to start unittest
# python -m unittest discover -s test