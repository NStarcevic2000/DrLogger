import os
import tempfile
import unittest

from pandas import DataFrame
from pandas.testing import assert_frame_equal

from util.config_enums import KEEP_SOURCE_FILE_LOCATION_ENUM

from processor.open_logs_processor import OpenLogsProcessor
from logs_managing.logs_manager import LogsManager
from logs_managing.logs_column_types import DataColumn, MetadataColumn
from logs_managing.reserved_names import RESERVED_COLUMN_NAMES as RColNameNS
from logs_managing.reserved_names import RESERVED_METADATA_NAMES as RMetaNS

from util.test_util import assert_columns_by_type

class TestOpenLogsProcessor(unittest.TestCase):
    def setUp(self):
        self.processor = OpenLogsProcessor()

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
        ret_columns = self.processor.process(
            data=self.tmp_file.name,
            keep_source_file_location_arg=KEEP_SOURCE_FILE_LOCATION_ENUM.FULL_PATH
        )
        # Assert columns by type
        expected_cols = [(DataColumn, RColNameNS.File), (DataColumn, RColNameNS.Message), (MetadataColumn, RMetaNS.General.OriginalLogs)]
        assert_columns_by_type(ret_columns, expected_cols)
        # Check the generated DataFrame
        result_df = LogsManager().simulate_rendered_data(ret_columns)
        expected_df = DataFrame(
            {RColNameNS.File: 3 * [self.tmp_file.name], RColNameNS.Message: ["Sample 1 abc", "Sample 2 def", "Sample 3 ghi"]}
        )
        assert_frame_equal(result_df, expected_df, check_dtype=False)

    def test_process_multiple_files(self):
        # Test processing multiple files
        tmp_file2 = tempfile.NamedTemporaryFile(delete=False, mode='w+', suffix='.log', encoding='utf-8')
        tmp_file2.writelines(["Sample 4 xyz\n", "Sample 5 mno\n"])
        tmp_file2.flush()
        tmp_file2.close()

        result_df =LogsManager().simulate_rendered_data(
            self.processor.process(
                data=[self.tmp_file.name, tmp_file2.name],
                keep_source_file_location_arg=KEEP_SOURCE_FILE_LOCATION_ENUM.FILE_ONLY
            )
        )
        expected_df = DataFrame(
            {
                RColNameNS.File: 3 * [os.path.basename(self.tmp_file.name)] + 2 * [os.path.basename(tmp_file2.name)],
                RColNameNS.Message: ["Sample 1 abc", "Sample 2 def", "Sample 3 ghi", "Sample 4 xyz", "Sample 5 mno"]
            }
        )
        try:
            assert_frame_equal(result_df, expected_df, check_dtype=False)
        finally:
            os.unlink(tmp_file2.name)
        

    def test_process_no_files(self):
        # Test processing with no files
        ret_columns = self.processor.process(
            data=[],
            keep_source_file_location_arg=KEEP_SOURCE_FILE_LOCATION_ENUM.NONE
        )
        # Assert columns by type
        assert ret_columns is None

    def test_process_short_path(self):
        # Test processing with Short Path
        ret_columns = self.processor.process(
            data=self.tmp_file.name,
            keep_source_file_location_arg=KEEP_SOURCE_FILE_LOCATION_ENUM.SHORT_PATH
        )
        expected_cols = [(DataColumn, RColNameNS.File), (DataColumn, RColNameNS.Message), (MetadataColumn, RMetaNS.General.OriginalLogs)]
        assert_columns_by_type(ret_columns, expected_cols)
        result_df = LogsManager().simulate_rendered_data(ret_columns)
        expected_df = DataFrame({
            RColNameNS.File: 3 * [os.path.basename(self.tmp_file.name)],
            RColNameNS.Message: ["Sample 1 abc", "Sample 2 def", "Sample 3 ghi"]
        })
        assert_frame_equal(result_df, expected_df, check_dtype=False)



    def test_line_endings_handling(self):
        # Create a file with Windows-style CRLF line endings using binary mode
        tmp_file_crlf = tempfile.NamedTemporaryFile(delete=False, mode='wb', suffix='.log')
        tmp_file_crlf.write(b"Line 1\r\nLine 2\r\nLine 3\r\n")
        tmp_file_crlf.flush()
        tmp_file_crlf.close()
        result_df = LogsManager().simulate_rendered_data(
            self.processor.process(
                data=tmp_file_crlf.name,
                keep_source_file_location_arg=KEEP_SOURCE_FILE_LOCATION_ENUM.FILE_ONLY
            )
        )
        expected_df = DataFrame(
            {RColNameNS.File: 3 * [os.path.basename(tmp_file_crlf.name)], RColNameNS.Message: ["Line 1", "Line 2", "Line 3"]}
        )
        assert_frame_equal(result_df, expected_df, check_dtype=False)
        os.unlink(tmp_file_crlf.name)
        
        # Create a file with Unix-style LF line endings using binary mode
        tmp_file_crlf = tempfile.NamedTemporaryFile(delete=False, mode='wb', suffix='.log')
        tmp_file_crlf.write(b"Line 1\nLine 2\nLine 3\n")
        tmp_file_crlf.flush()
        tmp_file_crlf.close()
        result_df = LogsManager().simulate_rendered_data(
            self.processor.process(
                data=tmp_file_crlf.name,
                keep_source_file_location_arg=KEEP_SOURCE_FILE_LOCATION_ENUM.FILE_ONLY
            )
        )
        expected_df = DataFrame(
            {RColNameNS.File: 3 * [os.path.basename(tmp_file_crlf.name)], RColNameNS.Message: ["Line 1", "Line 2", "Line 3"]}
        )
        try:
            assert_frame_equal(result_df, expected_df, check_dtype=False)
        finally:
            os.unlink(tmp_file_crlf.name)


# Run this command to start unittest
# python -m unittest discover -s test
