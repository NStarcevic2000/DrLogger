import unittest

from enum import Enum
from pandas import DataFrame
from pandas import Series
from pandas.testing import assert_frame_equal

from logs_managing.reserved_names import RESERVED_COLUMN_NAMES as RColNameNS
from logs_managing.reserved_names import RESERVED_METADATA_NAMES as RMetaNS
from logs_managing.logs_column_types import CaptureMessageColumn, DataColumn, MetadataColumn
from logs_managing.logs_manager import LogsManager

class TestLogsManager(unittest.TestCase):
    def test_simulate_rendered_data_errors(self):
        # Test error handling in simulate_rendered_data
        with self.assertRaises(ValueError):
            LogsManager().simulate_rendered_data("Not a valid input")  # cols is whatever

        with self.assertRaises(ValueError):
            LogsManager().simulate_rendered_data(
                list[1, 2, 3]
            )  # cols contains invalid types
        
        with self.assertRaises(ValueError):
            LogsManager().simulate_rendered_data(
                Series([1, 2, 3], name="InvalidSeries1"),
                Series([4, 5, 6], name="InvalidSeries2")
            )  # cols contains invalid types



    def test_simulate_rendered_data_only_data_column(self):
        # Test simulate_rendered_data with a simple DataFrame
        # Column created from DataFrame
        input_df = DataFrame({'Message': ['line1', 'line2', 'line3']})
        col_list = [DataColumn(input_df['Message'])]
        result_df = LogsManager().simulate_rendered_data(col_list)
        assert_frame_equal(result_df, input_df, check_dtype=False)
    
        # Test with no columns
        col_list = []
        result_df = LogsManager().simulate_rendered_data(col_list)
        assert_frame_equal(result_df, DataFrame())

        # Test with multiple data columns
        # Column created from DataFrame
        input_df = DataFrame({
            'Message': ['line1', 'line2', 'line3'],
            'Level': ['info', 'error', 'debug']
        })
        col_list = [DataColumn(input_df['Message']), DataColumn(input_df['Level'])]
        result_df = LogsManager().simulate_rendered_data(col_list)
        assert_frame_equal(result_df, input_df, check_dtype=False)

        # Test with new column created from a list
        col_list = [DataColumn(['A', 'B', 'C'], name='Category')]
        result_df = LogsManager().simulate_rendered_data(col_list)
        assert_frame_equal(result_df, DataFrame({
            'Category': ['A', 'B', 'C']
        }), check_dtype=False)

        # Test with starting DataFrame and column that modifies it
        # Order matters
        starting_df = DataFrame({
            'Message': ['line1', 'line2', 'line3']
        })
        col_list = [
            DataColumn(['A', 'B', 'C'], name='Category'),
            DataColumn(starting_df['Message'].str.upper(), name='Message')
        ]
        result_df = LogsManager().simulate_rendered_data(col_list)
        assert_frame_equal(result_df, DataFrame({
            'Category': ['A', 'B', 'C'],
            'Message': ['LINE1', 'LINE2', 'LINE3']
        }), check_dtype=False)

        # DataColumn is always casted to string
        col_list = [DataColumn([1, 2, 3], name='Numbers')]
        result_df = LogsManager().simulate_rendered_data(col_list)
        assert_frame_equal(result_df, DataFrame({
            'Numbers': ['1', '2', '3']
        }), check_dtype=False)



    def test_simulate_rendered_data_with_metadata(self):
        # Metadata is not kept in the final DataFrame, but we can test that processing works
        # Column created from DataFrame
        input_df = DataFrame({
            'Message': ['line1', 'line2', 'line3'],
            'Category': ['info', 'error', 'debug']
        })
        col_list = [
            DataColumn(input_df['Message']),
            MetadataColumn(input_df['Category'])
        ]
        result_df = LogsManager().simulate_rendered_data(col_list)
        expected_df = DataFrame({
            'Message': ['line1', 'line2', 'line3']
        })
        assert_frame_equal(result_df, expected_df, check_dtype=False)
    


    def test_simulate_rendered_data_with_collapsing_rows(self):
        # Test simulate_rendered_data with collapsing rows
        input_df = DataFrame({
            'Message': ['line1', 'line2', 'line3', 'line4', 'line5'],
            'Category': ['info', 'error', 'debug', 'info', 'error'],
            'Collapsing Rows': [None, None, 'line3', None, None]
        })
        col_list = [
            DataColumn(input_df['Message']),
            MetadataColumn(input_df['Category']),
            CaptureMessageColumn(input_df['Collapsing Rows'], name="Collapsing Rows", replace='<Collapsed {count}>')
        ]
        result_df = LogsManager().simulate_rendered_data(col_list)
        expected_df = DataFrame({
            'Message': ['<Collapsed 2>', 'line3', '<Collapsed 2>']
        })
        print(result_df)
        assert_frame_equal(result_df.reset_index(drop=True), expected_df, check_dtype=False)

    

    def test_simulate_rendered_data_with_all_columns(self):
        # Test real-life scenario with all column types
        col_list = [
            CaptureMessageColumn([None, 'Random Message2', None], name="Collapsing Rows", replace="<Collapsed>"),
            DataColumn(['Sender1', 'Sender2', 'Sender3'], name='From'),
            DataColumn(['Receiver1', 'Receiver2', 'Receiver3'], name='To'),
            DataColumn(['Success', 'Failed', 'Success'], name='Category'),
            DataColumn(['Random Message1', 'Random Message2', 'Random Message3'], name='Message'),
            MetadataColumn(['TCP', 'UDP', 'TCP'], name='Protocol', category='Network')
        ]

        result_df = LogsManager().simulate_rendered_data(col_list)
        expected_df = DataFrame({
            'From': ['Sender1', 'Sender2', 'Sender3'],
            'To': ['Receiver1', 'Receiver2', 'Receiver3'],
            'Category': ['Success', 'Failed', 'Success'],
            'Message': ['<Collapsed>', 'Random Message2', '<Collapsed>']
        })
        assert_frame_equal(result_df, expected_df, check_dtype=False)


        col_list = [
            DataColumn(['A', 'B', 'C', 'D', 'E', 'F'], name='Letters'),
            DataColumn(['1', '2', '3', '4', '5', '6'], name='Numbers'),
            MetadataColumn(['Success', 'Failed', 'Success', 'Failed', 'Success', 'Failed'], name='Category'),
            DataColumn(['Message1', 'Message2', 'Message3', 'Message4', 'Message5', 'Message6'], name='Message'),
            CaptureMessageColumn([None, None, '<Special Override Message>', 'Message4', 'Message5', None], name="Collapsing Rows", replace="<Collapsed>"),
        ]
        result_df = LogsManager().simulate_rendered_data(col_list)
        expected_df = DataFrame({
            'Letters': ['C', 'D', 'E', 'F'],
            'Numbers': ['3', '4', '5', '6'],
            'Message': ['<Special Override Message>', 'Message4', 'Message5', '<Collapsed>']
        })
        assert_frame_equal(result_df.reset_index(drop=True), expected_df, check_dtype=False)
    


    def test_logs_manager_through_stages(self):
        LogsManager().erase_data()
        visible_df, metadata_df = LogsManager().get_data(), LogsManager().get_metadata()
        assert isinstance(visible_df, DataFrame) and visible_df.empty
        assert isinstance(metadata_df, Series) and metadata_df.empty

        # Add initial data
        input_df = DataFrame({
            'Message': ['line1', 'line2', 'line3'],
            'Level': ['info', 'error', 'debug']
        })
        LogsManager().add_new_columns([
            DataColumn(input_df['Message'], name='Message'),
            MetadataColumn(input_df['Level'], name='Level')
        ])
        visible_df = LogsManager().get_data()
        assert_frame_equal(visible_df, DataFrame({
            'Message': ['line1', 'line2', 'line3']
        }), check_dtype=False)

        # Add more columns
        LogsManager().add_new_columns([
            DataColumn(['A', 'B', 'C'], name='Category')
        ])
        visible_df = LogsManager().get_data()
        assert_frame_equal(visible_df, DataFrame({
            'Message': ['line1', 'line2', 'line3'],
            'Category': ['A', 'B', 'C']
        }), check_dtype=False)

        # Modify existing column
        LogsManager().add_new_columns([
            DataColumn(input_df['Message'].str.upper(), name='Message')
        ])
        visible_df = LogsManager().get_data()
        assert_frame_equal(visible_df, DataFrame({
            'Category': ['A', 'B', 'C'],
            'Message': ['LINE1', 'LINE2', 'LINE3'],
        }), check_dtype=False)

        # Collapse rows
        LogsManager().add_new_columns([
            CaptureMessageColumn([None, 'LINE2', None], name="Collapsing Rows", replace="<Collapsed>"),
        ])
        visible_df = LogsManager().get_data()
        assert_frame_equal(visible_df, DataFrame({
            'Category': ['A', 'B', 'C'],
            'Message': ['<Collapsed>', 'LINE2', '<Collapsed>'],
        }), check_dtype=False)
