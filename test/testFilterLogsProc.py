import unittest
from util.configStore import ConfigStore, Config
from configStoreImpl import CONTEXTUALIZE_LINES_ENUM
from enum import Enum
from pandas import DataFrame
from pandas.testing import assert_frame_equal
from processor.filterLogsProc import FilterLogsProcess

class TestFilterLogsProcess(unittest.TestCase):
    def setUp(self):
        self.cs = ConfigStore("sample_config_store",
            ConfigStore("filter_logs",
                Config("filter_enabled", True, type_of=bool),
                Config("filter_pattern", [], type_of=list, element_type=str),
                Config("contextualize_lines", CONTEXTUALIZE_LINES_ENUM, type_of=Enum),
                Config("contextualize_lines_count", 5, type_of=int),
                Config("keep_hidden_logs", True, type_of=bool),
            )
        )
        # For testing, we can set the keep_hidden_logs to False
        # to ensure we are testing the filtering logic
        self.cs.set(self.cs.r.filter_logs.keep_hidden_logs, False)
        self.processor = FilterLogsProcess(self.cs)

    def test_process_invalid_input(self):
        # Test with non-DataFrame input
        with self.assertRaises(ValueError):
            self.processor.process("not a dataframe")

    def test_process_no_filter_patterns(self):
        # Test when no filter patterns are provided
        self.cs.set(self.cs.r.filter_logs.filter_pattern, [])
        input_df = DataFrame({'Message': ['line1', 'line2', 'line3']})
        result_df = self.processor.process(input_df)
        assert_frame_equal(result_df, input_df)

    def test_process_basic_filtering(self):
        # Test basic pattern filtering
        self.cs.set(self.cs.r.filter_logs.filter_pattern, [["Message", "error"]])
        self.cs.set(self.cs.r.filter_logs.contextualize_lines, CONTEXTUALIZE_LINES_ENUM.NONE.value)
        self.cs.set(self.cs.r.filter_logs.contextualize_lines_count, 0)

        input_df = DataFrame({'Message': ['info message', 'error occurred', 'debug info']})
        result_df = self.processor.process(input_df)
        
        expected_df = DataFrame({'Message': ['error occurred']})
        try:
            assert_frame_equal(result_df.reset_index(drop=True), expected_df)
        except AssertionError as e:
            print("Assertion failed:", e)
            print("Result DataFrame:\n", result_df)
            print("Expected DataFrame:\n", expected_df)
            raise

    def test_process_with_contextualization(self):
        # Test contextualization of filtered lines
        self.cs.set(self.cs.r.filter_logs.filter_pattern, [["Message", "error"]])
        self.cs.set(self.cs.r.filter_logs.contextualize_lines, CONTEXTUALIZE_LINES_ENUM.LINES_BEFORE_AND_AFTER.value)
        self.cs.set(self.cs.r.filter_logs.contextualize_lines_count, 1)

        input_df = DataFrame({'Message': ['line1', 'line2', 'error occurred', 'line4', 'line5']})
        result_df = self.processor.process(input_df)
        
        expected_df = DataFrame({
            'Message': ['line2', 'error occurred', 'line4'],
        })
        assert_frame_equal(result_df.reset_index(drop=True), expected_df)

    def test_process_multiple_patterns(self):
        # Test filtering with multiple patterns
        self.cs.set(self.cs.r.filter_logs.filter_pattern, [["", "warning"], ["Type", "type3"]])
        self.cs.set(self.cs.r.filter_logs.contextualize_lines_count, 0)

        input_df = DataFrame({
            'Message': ['line1 error', 'line2 warning', 'line3 info', 'line4 error'],
            'Type': ['line1 type1', 'line2 type2', 'line3 type3', 'line4 type4']
        })
        result_df = self.processor.process(input_df)
        
        # Should match row with both error in Message AND warning in Type (none in this case)
        expected_df = DataFrame({
            'Message': ['line2 warning', 'line3 info'],
            'Type': ['line2 type2', 'line3 type3']
        })
        try:
            assert_frame_equal(result_df.reset_index(drop=True), expected_df)
        except AssertionError as e:
            print("Assertion failed:", e)
            print("Result DataFrame:\n", result_df)
            print("Expected DataFrame:\n", expected_df)
            raise



    def test_process_empty_dataframe(self):
        # Test with empty DataFrame
        self.cs.set(self.cs.r.filter_logs.filter_pattern, [["Message", "error"]])
        input_df = DataFrame({'Message': []})
        result_df = self.processor.process(input_df)
        
        expected_df = DataFrame({'Message': []})
        assert_frame_equal(result_df, expected_df)



    def test_process_skip_empty_patterns(self):
        # Test skipping empty patterns
        self.cs.set(self.cs.r.filter_logs.filter_pattern, [["", ""], ["Message", "error"]])
        self.cs.set(self.cs.r.filter_logs.contextualize_lines_count, 0)

        input_df = DataFrame({'Message': ['info message', 'error occurred', 'debug info']})
        result_df = self.processor.process(input_df)
        
        expected_df = DataFrame({'Message': ['error occurred']})
        try:
            assert_frame_equal(result_df.reset_index(drop=True), expected_df)
        except AssertionError as e:
            print("Assertion failed:", e)
            print("Result DataFrame:\n", result_df)
            print("Expected DataFrame:\n", expected_df)
            raise



    def test_process_default_message_column(self):
        # Test using default Message column when pattern_column is empty
        self.cs.set(self.cs.r.filter_logs.filter_pattern, [["", "error"]])
        self.cs.set(self.cs.r.filter_logs.contextualize_lines_count, 0)

        input_df = DataFrame({'Message': ['info message', 'error occurred', 'debug info']})
        result_df = self.processor.process(input_df)
        
        expected_df = DataFrame({'Message': ['error occurred']})
        try:
            assert_frame_equal(result_df.reset_index(drop=True), expected_df)
        except AssertionError as e:
            print("Assertion failed:", e)
            print("Result DataFrame:\n", result_df)
            print("Expected DataFrame:\n", expected_df)
            raise