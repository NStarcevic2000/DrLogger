import unittest

import tempfile
from enum import Enum
from pandas import DataFrame
from pandas.testing import assert_frame_equal

from processor.split_log_lines_processor import SplitLogLinesProcessor
from util.logs_manager import LogsManager

class TestSplitLogLinesProcessor(unittest.TestCase):
    def setUp(self):
        self.processor = SplitLogLinesProcessor()

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
        input_df = DataFrame({'Message': ["Sample 1:abc", "Sample 2:def", "Sample 3:ghi"]})
        result_df =LogsManager().simulate_rendered_data(
            self.processor.process(input_df.copy(),
                                   pattern_format_arg="<Group1> <Group2>:<Group3>",
                                   timestamp_format_arg=""),
            visible_df=input_df
        )

        expected_df = DataFrame({
            'Group1': ["Sample", "Sample", "Sample"],
            'Group2': ["1", "2", "3"],
            'Group3': ["abc", "def", "ghi"],
            'Message': ["", "", ""]
        })

        assert_frame_equal(result_df, expected_df)

    def test_empty_dataframe(self):
        # Test processing an empty DataFrame
        input_df = DataFrame({'Message': []})
        result_df =LogsManager().simulate_rendered_data(
            self.processor.process(input_df.copy(),
                                   pattern_format_arg="<Group1> <Group2>:<Group3>",
                                   timestamp_format_arg=""),
            visible_df=input_df.copy()
        )
        assert_frame_equal(result_df, input_df)
    
    def test_timestamp_format(self):
        # Test processing with timestamp format
        input_df = DataFrame({'Message': ["2023-10-01 12:00:00 Sample 1:abc", "2023-10-01 12:01:00 Sample 2:def", "2023-10-01 12:02:00 Sample 3:ghi"]})
        result_df = LogsManager().simulate_rendered_data(
            self.processor.process(input_df.copy(),
                pattern_format_arg="<Year>-<Month>-<Day> <Hour>:<Minutes>:<Seconds> <Type> <From>:",
                timestamp_format_arg="<Year>-<Month>-<Day> <Hour>:<Minutes>:<Seconds>"),
            visible_df=input_df.copy()
        )

        expected_df = DataFrame({
            'Timestamp': ["2023-10-01 12:00:00", "2023-10-01 12:01:00", "2023-10-01 12:02:00"],
            'Type': ["Sample", "Sample", "Sample"],
            'From': ["1", "2", "3"],
            'Message': ["abc", "def", "ghi"]
        })
        assert_frame_equal(result_df, expected_df)