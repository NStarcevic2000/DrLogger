import unittest

from enum import Enum
from pandas import DataFrame
from pandas.testing import assert_frame_equal

from util.config_enums import CONTEXTUALIZE_LINES_ENUM
from processor.filter_logs_processor import FilterLogsProcessor
from util.logs_manager import LogsManager

class TestFilterLogsProcessor(unittest.TestCase):
    def setUp(self):
        self.processor = FilterLogsProcessor()

    def test_process_invalid_input(self):
        # Test with non-DataFrame input
        with self.assertRaises(ValueError):
            self.processor.process("not a dataframe")

    def test_process_no_filter_patterns(self):
        # Test when no filter patterns are provided
        input_df = DataFrame({'Message': ['line1', 'line2', 'line3']})
        result_df = self.processor.process(input_df,
            filter_pattern_arg=[],
            contextualize_lines_count_arg=0,
            contextualize_lines_type_arg=CONTEXTUALIZE_LINES_ENUM.NONE.value,
            keep_hidden_logs_arg=False
        )
        assert_frame_equal(result_df, input_df)

    def test_process_basic_filtering(self):
        # Test basic pattern filtering
        input_df = DataFrame({'Message': ['info message', 'error occurred', 'debug info']})
        result_df = LogsManager().simulate_rendered_data_for_cols(
            self.processor.process(input_df,
                filter_pattern_arg=[["Message", "error"]],
                contextualize_lines_count_arg=0,
                contextualize_lines_type_arg=CONTEXTUALIZE_LINES_ENUM.LINES_BEFORE_AND_AFTER,
                keep_hidden_logs_arg=False
            )
        )
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
        input_df = DataFrame({'Message': ['info message', 'error occurred', 'debug info']})
        result_df = LogsManager().simulate_rendered_data_for_cols(
            self.processor.process(input_df,
                filter_pattern_arg=[["Message", "error"]],
                contextualize_lines_count_arg=1,
                contextualize_lines_type_arg=CONTEXTUALIZE_LINES_ENUM.LINES_BEFORE_AND_AFTER,
                keep_hidden_logs_arg=False
            )
        )
        expected_df = DataFrame({
            'Message': ['info message', 'error occurred', 'debug info'],
        })
        assert_frame_equal(result_df.reset_index(drop=True), expected_df)

        input_df = DataFrame({'Message': ['line1', 'line2', 'error occurred', 'line4', 'line5']})
        result_df = LogsManager().simulate_rendered_data_for_cols(
            self.processor.process(input_df,
                filter_pattern_arg=[["Message", "error"]],
                contextualize_lines_count_arg=1,
                contextualize_lines_type_arg=CONTEXTUALIZE_LINES_ENUM.LINES_BEFORE_AND_AFTER,
                keep_hidden_logs_arg=False
            )
        )
        expected_df = DataFrame({
            'Message': ['line2', 'error occurred', 'line4'],
        })
        assert_frame_equal(result_df.reset_index(drop=True), expected_df)

        # With 0, it will behave as a type specified NONE = Only filtered lines are kept, no context
        input_df = DataFrame({'Message': ['line1', 'line2', 'error occurred', 'line4', 'line5']})
        result_df = self.processor.process(input_df,
            filter_pattern_arg=[["Message", "error"]],
            contextualize_lines_count_arg=0,
            contextualize_lines_type_arg=CONTEXTUALIZE_LINES_ENUM.LINES_BEFORE_AND_AFTER,
            keep_hidden_logs_arg=False
        )
        expected_df = DataFrame({
            'Message': ['error occurred'],
        })
        assert_frame_equal(result_df.reset_index(drop=True), expected_df)

    def test_process_multiple_patterns(self):
        # Test filtering with multiple patterns
        # Should match row with both error in Message AND warning in Type (none in this case)
        input_df = DataFrame({
            'Message': ['line1 error', 'line2 warning', 'line3 info', 'line4 error'],
            'Type': ['line1 type1', 'line2 type2', 'line3 type3', 'line4 type4']
        }).reset_index(drop=True)
        result_df = LogsManager().simulate_rendered_data_for_cols(
            self.processor.process(input_df,
                filter_pattern_arg=[["Message", "warning"], ["Type", "type3"]],
                contextualize_lines_count_arg=0,
                contextualize_lines_type_arg=CONTEXTUALIZE_LINES_ENUM.NONE,
                keep_hidden_logs_arg=False
            )
        ).reset_index(drop=True)
        expected_df = DataFrame({
            'Message': ['line2 warning', 'line3 info'],
            'Type': ['line2 type2', 'line3 type3']
        }).reset_index(drop=True)
        try:
            assert_frame_equal(result_df, expected_df)
        except AssertionError as e:
            print("Assertion failed:", e)
            print("Result DataFrame:\n", result_df)
            print("Expected DataFrame:\n", expected_df)
            raise



    def test_process_empty_dataframe(self):
        # Test with empty DataFrame
        input_df = DataFrame({'Message': []})
        result_df = LogsManager().simulate_rendered_data_for_cols(
            self.processor.process(input_df,
                filter_pattern_arg=[["Message", "error"]],
                contextualize_lines_count_arg=0,
                contextualize_lines_type_arg=CONTEXTUALIZE_LINES_ENUM.NONE,
                keep_hidden_logs_arg=False
            )
        )
        expected_df = DataFrame({'Message': []})
        assert_frame_equal(result_df, expected_df)



    def test_process_skip_empty_patterns(self):
        # Test skipping empty patterns
        input_df = DataFrame({'Message': ['info message', 'error occurred', 'debug info']})
        result_df = LogsManager().simulate_rendered_data_for_cols(
            self.processor.process(input_df,
                filter_pattern_arg=[["", ""], ["Message", "error"]],
                contextualize_lines_count_arg=0,
                contextualize_lines_type_arg=CONTEXTUALIZE_LINES_ENUM.NONE,
                keep_hidden_logs_arg=False
            )
        )
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
        input_df = DataFrame({'Message': ['info message', 'error occurred', 'debug info']})
        result_df = LogsManager().simulate_rendered_data_for_cols(
            self.processor.process(input_df,
                filter_pattern_arg=[["", "error"]],
                contextualize_lines_count_arg=0,
                contextualize_lines_type_arg=CONTEXTUALIZE_LINES_ENUM.NONE,
                keep_hidden_logs_arg=False
            )
        )
        expected_df = DataFrame({'Message': ['error occurred']})
        try:
            assert_frame_equal(result_df.reset_index(drop=True), expected_df)
        except AssertionError as e:
            print("Assertion failed:", e)
            print("Result DataFrame:\n", result_df)
            print("Expected DataFrame:\n", expected_df)
            raise