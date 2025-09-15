import unittest

from enum import Enum
from pandas import DataFrame
from pandas.testing import assert_frame_equal

from util.config_enums import CONTEXTUALIZE_LINES_ENUM
from processor.filter_logs_processor import FilterLogsProcessor, FILTERED_LINE
from logs_managing.logs_manager import LogsManager
from logs_managing.logs_column_types import CollapsingRowsColumn, DataColumn
from util.test_util import assert_columns_by_type

class TestFilterLogsProcessor(unittest.TestCase):
    def setUp(self):
        self.processor = FilterLogsProcessor()

    def test_process_no_filter_patterns(self):
        # Test when no filter patterns are provided
        input_df = DataFrame({'Message': ['line1', 'line2', 'line3']})
        ret_columns = self.processor.process(input_df.copy(),
            filter_pattern_arg=[],
            contextualize_lines_count_arg=0,
            contextualize_lines_type_arg=CONTEXTUALIZE_LINES_ENUM.NONE
        )
        assert ret_columns is None

    def test_process_basic_filtering(self):
        # Test basic pattern filtering
        input_df = DataFrame({'Message': ['info message', 'error occurred', 'debug info']})
        ret_columns = self.processor.process(input_df.copy(),
            filter_pattern_arg=[["Message", "error"]],
            contextualize_lines_count_arg=0,
            contextualize_lines_type_arg=CONTEXTUALIZE_LINES_ENUM.LINES_BEFORE_AND_AFTER
        )
        expected_columns = [(CollapsingRowsColumn, FILTERED_LINE)]
        assert_columns_by_type(ret_columns, expected_columns)
        assert [True, False, True] == ret_columns[0].tolist()
        result_df = LogsManager().simulate_rendered_data([
            DataColumn(input_df['Message'], name='Message'),
            CollapsingRowsColumn([True, False, True], name='Show Filtered Only', collapse_heading_pattern="<Filtered {count} row(s)>")
        ])
        expected_df = DataFrame({
            'Message': ['<Filtered 1 row(s)>', 'error occurred', '<Filtered 1 row(s)>'],
        })
        assert_frame_equal(result_df, expected_df, check_dtype=False)

    def test_process_with_contextualization(self):
        # Test contextualization of filtered lines
        input_df = DataFrame({'Message': ['info message', 'error occurred', 'debug info']})
        ret_columns = self.processor.process(input_df.copy(),
            filter_pattern_arg=[["Message", "error"]],
            contextualize_lines_count_arg=1,
            contextualize_lines_type_arg=CONTEXTUALIZE_LINES_ENUM.LINES_BEFORE_AND_AFTER
        )
        expected_columns = [(CollapsingRowsColumn, FILTERED_LINE)]
        assert_columns_by_type(ret_columns, expected_columns)
        result_df = LogsManager().simulate_rendered_data([
            DataColumn(input_df['Message'])
        ]+ret_columns)
        expected_df = DataFrame({
            'Message': ['info message', 'error occurred', 'debug info'],
        })
        assert_frame_equal(result_df, expected_df, check_dtype=False)



        input_df = DataFrame({'Message': ['line1', 'line2', 'error occurred', 'line4', 'line5']})
        ret_columns = self.processor.process(input_df.copy(),
            filter_pattern_arg=[["Message", "error"]],
            contextualize_lines_count_arg=1,
            contextualize_lines_type_arg=CONTEXTUALIZE_LINES_ENUM.LINES_BEFORE_AND_AFTER
        )
        expected_columns = [(CollapsingRowsColumn, FILTERED_LINE)]
        assert_columns_by_type(ret_columns, expected_columns)
        result_df = LogsManager().simulate_rendered_data([
            DataColumn(input_df['Message'])
        ]+ret_columns)
        expected_df = DataFrame({
            'Message': ['<Filtered 1 row(s)>', 'line2', 'error occurred', 'line4', '<Filtered 1 row(s)>'],
        })
        assert_frame_equal(result_df, expected_df, check_dtype=False)

        # With 0, it will behave as a type specified NONE = Only filtered lines are kept, no context
        input_df = DataFrame({'Message': ['line1', 'line2', 'error occurred', 'line4', 'line5']})
        ret_columns = self.processor.process(input_df.copy(),
            filter_pattern_arg=[["Message", "error"]],
            contextualize_lines_count_arg=0,
            contextualize_lines_type_arg=CONTEXTUALIZE_LINES_ENUM.LINES_BEFORE_AND_AFTER
        )
        expected_columns = [(CollapsingRowsColumn, FILTERED_LINE)]
        assert_columns_by_type(ret_columns, expected_columns)
        result_df = LogsManager().simulate_rendered_data(
            ret_columns,
            starting_visible_df=input_df.copy()
        )
        expected_df = DataFrame({
            'Message': ['error occurred'],
        })
        assert_frame_equal(result_df, expected_df, check_dtype=False)

    def test_process_multiple_patterns(self):
        # Test filtering with multiple patterns
        # Should match row with both error in Message AND warning in Type (none in this case)
        input_df = DataFrame({
            'Message': ['line1 error', 'line2 warning', 'line3 info', 'line4 error'],
            'Type': ['line1 type1', 'line2 type2', 'line3 type3', 'line4 type4']
        }).reset_index(drop=True)
        ret_columns = self.processor.process(input_df.copy(),
            filter_pattern_arg=[["Message", "warning"], ["Type", "type3"]],
            contextualize_lines_count_arg=0,
            contextualize_lines_type_arg=CONTEXTUALIZE_LINES_ENUM.NONE
        )
        expected_columns = [(CollapsingRowsColumn, FILTERED_LINE)]
        assert_columns_by_type(ret_columns, expected_columns)
        result_df = LogsManager().simulate_rendered_data([
            DataColumn(input_df['Message']),
            DataColumn(input_df['Type'])
        ]+ret_columns)
        expected_df = DataFrame({
            'Message': ['line2 warning', 'line3 info'],
            'Type': ['line2 type2', 'line3 type3']
        })
        assert_frame_equal(result_df, expected_df, check_dtype=False)

    def test_process_empty_dataframe(self):
        # Test with empty DataFrame
        input_df = DataFrame({'Message': []})
        ret_columns = self.processor.process(input_df.copy(),
            filter_pattern_arg=[["Message", "error"]],
            contextualize_lines_count_arg=0,
            contextualize_lines_type_arg=CONTEXTUALIZE_LINES_ENUM.NONE
        )
        assert ret_columns is None

    def test_process_skip_empty_patterns(self):
        # Test skipping empty patterns
        input_df = DataFrame({'Message': ['info message', 'error occurred', 'debug info']})
        ret_columns = self.processor.process(input_df.copy(),
            filter_pattern_arg=[["", ""], ["Message", "error"]],
            contextualize_lines_count_arg=0,
            contextualize_lines_type_arg=CONTEXTUALIZE_LINES_ENUM.NONE
        )
        expected_columns = [(CollapsingRowsColumn, FILTERED_LINE)]
        assert_columns_by_type(ret_columns, expected_columns)
        result_df = LogsManager().simulate_rendered_data([
            DataColumn(input_df['Message'])
        ]+ret_columns)
        expected_df = DataFrame({
            'Message': ['<Filtered 1 row(s)>', 'error occurred', '<Filtered 1 row(s)>'],
        })
        assert_frame_equal(result_df, expected_df, check_dtype=False)

    def test_process_default_message_column(self):
        # Test using default Message column when pattern_column is empty
        input_df = DataFrame({'Message': ['info message', 'error occurred', 'debug info']})
        ret_columns = self.processor.process(input_df.copy(),
            filter_pattern_arg=[["", "error"]],
            contextualize_lines_count_arg=0,
            contextualize_lines_type_arg=CONTEXTUALIZE_LINES_ENUM.NONE
        )
        expected_columns = [(CollapsingRowsColumn, FILTERED_LINE)]
        assert_columns_by_type(ret_columns, expected_columns)
        result_df = LogsManager().simulate_rendered_data([
            DataColumn(input_df['Message'])
        ]+ret_columns)
        expected_df = DataFrame({'Message': ['error occurred']})
        assert_frame_equal(result_df, expected_df, check_dtype=False)
    
    def test_process_with_hidden_logs_kept(self):
        input_df = DataFrame({'Message': ['info message', 'error occurred', 'debug info']})
        ret_columns = self.processor.process(input_df.copy(),
            filter_pattern_arg=[["Message", "error"]],
            contextualize_lines_count_arg=0,
            contextualize_lines_type_arg=CONTEXTUALIZE_LINES_ENUM.NONE
        )
        expected_columns = [(CollapsingRowsColumn, FILTERED_LINE)]
        assert_columns_by_type(ret_columns, expected_columns)
        assert ret_columns[0].collapse_heading_pattern is not None
        result_df = LogsManager().simulate_rendered_data(
            [DataColumn(input_df['Message'])] + ret_columns,
        )
        print(result_df)
        # Only the second row is the same
        assert_frame_equal(
            result_df.iloc[1:2].reset_index(drop=True),
            input_df.iloc[1:2].reset_index(drop=True),
            check_dtype=False
        )
        # The first and last rows should be the collapsed headings
        # self.assertTrue(result_df.iloc[0, 0].startswith("< Filtered"))
        # self.assertTrue(result_df.iloc[2, 0].startswith("< Filtered"))