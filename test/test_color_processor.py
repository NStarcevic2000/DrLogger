import unittest
from pandas import DataFrame, Series
from pandas.testing import assert_frame_equal, assert_series_equal

from processor.color_logs_processor import ColorLogsProcessor
from logs_managing.reserved_names import RESERVED_COLUMN_NAMES as RColNameNS
from logs_managing.reserved_names import RESERVED_METADATA_NAMES as RMetaNS
from logs_managing.logs_column_types import MetadataColumn
from util.test_util import assert_columns_by_type

class TestColorLogsProccessor(unittest.TestCase):
    def setUp(self):
        self.processor = ColorLogsProcessor()

    def test_process_basic_coloring_pattern(self):
        # Test when no filter patterns are provided
        input_df = DataFrame({RColNameNS.Message: ['line1', 'line2', 'line3']})
        ret_columns = self.processor.process(input_df.copy(),
            color_scheme_arg=[
                [RColNameNS.Message, "line1", "#FF0000", "#FFFF00"],
                [RColNameNS.Message, "line2", "#00FF00", "#0000FF"]
            ]
        )
        expected_columns = [(MetadataColumn, RMetaNS.General.ForegroundColor), (MetadataColumn, RMetaNS.General.BackgroundColor)]
        assert_columns_by_type(ret_columns, expected_columns)
        expected_fg = ['#FF0000', '#00FF00', '#000000']
        expected_bg = ['#FFFF00', '#0000FF', '#FFFFFF']
        assert list(ret_columns[0]) == expected_fg, f"Expected {expected_fg}, got {list(ret_columns[0])}"
        assert list(ret_columns[1]) == expected_bg, f"Expected {expected_bg}, got {list(ret_columns[1])}"

    def test_process_no_matching_patterns(self):
        # Test when no patterns match
        input_df = DataFrame({RColNameNS.Message: ['line1', 'line2', 'line3']})
        ret_columns = self.processor.process(input_df.copy(),
            color_scheme_arg=[
                [RColNameNS.Message, "nomatch", "#FF0000", "#FFFF00"]
            ]
        )
        expected_columns = [(MetadataColumn, RMetaNS.General.ForegroundColor), (MetadataColumn, RMetaNS.General.BackgroundColor)]
        assert_columns_by_type(ret_columns, expected_columns)
        expected_fg = ['#000000', '#000000', '#000000']
        expected_bg = ['#FFFFFF', '#FFFFFF', '#FFFFFF']
        assert list(ret_columns[0]) == expected_fg, f"Expected {expected_fg}, got {list(ret_columns[0])}"
        assert list(ret_columns[1]) == expected_bg, f"Expected {expected_bg}, got {list(ret_columns[1])}"
    
    def test_process_apply_to_any_column(self):
        input_df = DataFrame({
            RColNameNS.Message: ['line1', 'line2', 'line3'],
            'OtherColumn': ['alpha', 'beta', 'gamma']
        })
        ret_columns = self.processor.process(input_df.copy(),
            color_scheme_arg=[
                ["", "beta", "#123456", "#654321"]
            ]
        )
        expected_columns = [(MetadataColumn, RMetaNS.General.ForegroundColor), (MetadataColumn, RMetaNS.General.BackgroundColor)]
        assert_columns_by_type(ret_columns, expected_columns)
        expected_fg = ['#000000', '#123456', '#000000']
        expected_bg = ['#FFFFFF', '#654321', '#FFFFFF']
        assert list(ret_columns[0]) == expected_fg, f"Expected {expected_fg}, got {list(ret_columns[0])}"
        assert list(ret_columns[1]) == expected_bg, f"Expected {expected_bg}, got {list(ret_columns[1])}"

    def test_process_empty_dataframe(self):
        input_df = DataFrame({RColNameNS.Message: []})
        ret_columns = self.processor.process(input_df.copy(),
            color_scheme_arg=[
                [RColNameNS.Message, "line1", "#FF0000", "#FFFF00"]
            ]
        )
        self.assertIsNone(ret_columns)
    
    def test_process_missing_message_column(self):
        input_df = DataFrame({'OtherColumn': ['line1', 'line2', 'line3']})
        ret_columns = self.processor.process(input_df.copy(),
            color_scheme_arg=[
                [RColNameNS.Message, "line1", "#FF0000", "#FFFF00"]
            ]
        )
        self.assertIsNone(ret_columns)
    
    def test_process_no_color_scheme(self):
        input_df = DataFrame({RColNameNS.Message: ['line1', 'line2', 'line3']})
        ret_columns = self.processor.process(input_df.copy(),
            color_scheme_arg=[]
        )
        expected_columns = [(MetadataColumn, RMetaNS.General.ForegroundColor), (MetadataColumn, RMetaNS.General.BackgroundColor)]
        assert_columns_by_type(ret_columns, expected_columns)
        expected_fg = ['#000000', '#000000', '#000000']
        expected_bg = ['#FFFFFF', '#FFFFFF', '#FFFFFF']
        assert list(ret_columns[0]) == expected_fg, f"Expected {expected_fg}, got {list(ret_columns[0])}"
        assert list(ret_columns[1]) == expected_bg, f"Expected {expected_bg}, got {list(ret_columns[1])}"