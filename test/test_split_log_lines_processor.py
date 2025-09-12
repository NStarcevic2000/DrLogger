import unittest

import tempfile
from enum import Enum
from pandas import DataFrame
from pandas.testing import assert_frame_equal

from processor.split_log_lines_processor import SplitLogLinesProcessor
from util.logs_manager import LogsManager
from util.logs_column import CollapsingRowsColumn, DataColumn, MetadataColumn

from util.test_util import assert_columns_by_type

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
        input_df = DataFrame({'Message': ["Sample 1:abc", "Sample 2:def", "Sample 3:ghi"]})
        ret_columns = self.processor.process(
            input_df.copy(),
            pattern_format_arg="<Group1> <Group2>:<Group3>",
            timestamp_format_arg=""
        )
        # Assert column names and types
        expected_columns = [(DataColumn, 'Group1'), (DataColumn, 'Group2'), (DataColumn, 'Group3'), (DataColumn, 'Message')]
        assert_columns_by_type(ret_columns, expected_columns)

        # Test simulate_rendered_data
        result_df = LogsManager().simulate_rendered_data(ret_columns)
        expected_df = DataFrame({
            'Group1': ["Sample", "Sample", "Sample"],
            'Group2': ["1", "2", "3"],
            'Group3': ["abc", "def", "ghi"],
            'Message': ["", "", ""]
        })
        assert_frame_equal(result_df, expected_df)

    def test_empty_dataframe(self):
        input_df = DataFrame({'Message': []})
        ret_columns = self.processor.process(
            input_df.copy(),
            pattern_format_arg="<Group1> <Group2>:<Group3>",
            timestamp_format_arg=""
        )

        # Assert column names and types
        assert ret_columns is None

    def test_timestamp_format(self):
        input_df = DataFrame({
            'Message': [
                "2023-10-01 12:00:00 Sample 1:abc",
                "2023-10-01 12:01:00 Sample 2:def",
                "2023-10-01 12:02:00 Sample 3:ghi"
            ]
        })
        ret_columns = self.processor.process(
            input_df.copy(),
            pattern_format_arg="<Year>-<Month>-<Day> <Hour>:<Minutes>:<Seconds> <Type> <From>:",
            timestamp_format_arg="<Year>-<Month>-<Day> <Hour>:<Minutes>:<Seconds>"
        )

        # Assert column names and types
        expected_columns = [(DataColumn, 'Timestamp'), (DataColumn, 'Type'), (DataColumn, 'From'), (DataColumn, 'Message')]
        assert_columns_by_type(ret_columns, expected_columns)

        # Test simulate_rendered_data
        result_df = LogsManager().simulate_rendered_data(ret_columns)
        expected_df = DataFrame({
            'Timestamp': ["2023-10-01 12:00:00", "2023-10-01 12:01:00", "2023-10-01 12:02:00"],
            'Type': ["Sample", "Sample", "Sample"],
            'From': ["1", "2", "3"],
            'Message': ["abc", "def", "ghi"]
        })
        assert_frame_equal(result_df, expected_df)