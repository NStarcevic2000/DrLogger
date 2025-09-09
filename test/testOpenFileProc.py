import tempfile
import unittest

from pandas import DataFrame
from pandas.testing import assert_frame_equal
from enum import Enum

from util.config_store import Config, ConfigStore
from util.config_enums import KEEP_SOURCE_FILE_LOCATION_ENUM

from processor.open_logs_processor import OpenLogsProcess

class TestOpenLogsProcess(unittest.TestCase):
    def setUp(self):
        self.processor = OpenLogsProcess()

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

    def test_process_single_file(self):
        # Test processing a single file
        result_df = self.processor.process(
            data=self.tmp_file.name,
            keep_source_file_location_arg=KEEP_SOURCE_FILE_LOCATION_ENUM.FULL_PATH.value
        )

        self.assertIsInstance(result_df, DataFrame)
        self.assertEqual(len(result_df), 3)
        expected_df = DataFrame(
            {'File': 3 * [self.tmp_file.name], 'Line': ["Sample 1 abc", "Sample 2 def", "Sample 3 ghi"]}
        )
        assert_frame_equal(result_df, expected_df)

    def test_process_multiple_files(self):
        # Test processing multiple files
        tmp_file2 = tempfile.NamedTemporaryFile(delete=False, mode='w+', suffix='.log', encoding='utf-8')
        tmp_file2.writelines(["Sample 4 xyz\n", "Sample 5 mno\n"])
        tmp_file2.flush()
        tmp_file2.close()

        result_df = self.processor.process(
            data=[self.tmp_file.name, tmp_file2.name],
            keep_source_file_location_arg=KEEP_SOURCE_FILE_LOCATION_ENUM.FILE_ONLY.value
        )

        self.assertIsInstance(result_df, DataFrame)
        self.assertEqual(len(result_df), 5)
        expected_df = DataFrame(
            {
                'File': 3 * [self.tmp_file.name] + 2 * [tmp_file2.name],
                'Line': ["Sample 1 abc", "Sample 2 def", "Sample 3 ghi", "Sample 4 xyz", "Sample 5 mno"]
            }
        )
        assert_frame_equal(result_df, expected_df)

        import os
        os.unlink(tmp_file2.name)

    def test_process_no_files(self):
        # Test processing with no files
        result_df = self.processor.process(
            data=[],
            keep_source_file_location_arg=KEEP_SOURCE_FILE_LOCATION_ENUM.NONE.value
        )

        self.assertIsInstance(result_df, DataFrame)
        self.assertEqual(len(result_df), 0)

    def test_process_short_path(self):
        # Test processing with Short Path
        result_df = self.processor.process(
            data=self.tmp_file.name,
            keep_source_file_location_arg=KEEP_SOURCE_FILE_LOCATION_ENUM.SHORT_PATH.value
        )

        self.assertIsInstance(result_df, DataFrame)
        self.assertEqual(len(result_df), 3)
        expected_df = DataFrame(
            {'File': 3 * [self.tmp_file.name.split('/')[-1]], 'Line': ["Sample 1 abc", "Sample 2 def", "Sample 3 ghi"]}
        )
        assert_frame_equal(result_df, expected_df)

    def test_read_cached_data(self):
        # Test reading cached data after processing
        self.processor.process(
            data=self.tmp_file.name,
            keep_source_file_location_arg=KEEP_SOURCE_FILE_LOCATION_ENUM.SHORT_PATH.value
        )
        cached_data = self.processor.read_cached_data()

        self.assertIsInstance(cached_data, DataFrame)
        self.assertEqual(len(cached_data), 3)
        expected_df = DataFrame(
            {'File': 3 * [self.tmp_file.name], 'Line': ["Sample 1 abc", "Sample 2 def", "Sample 3 ghi"]}
        )
        assert_frame_equal(cached_data, expected_df)


# Run this command to start unittest
# python -m unittest discover -s test
