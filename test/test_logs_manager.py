import unittest

from enum import Enum
from pandas import DataFrame
from pandas import Series
from pandas.testing import assert_frame_equal

from logs_managing.logs_column_types import CollapsingRowsColumn, DataColumn, MetadataColumn
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
        result_df = LogsManager().simulate_rendered_data(col_list, starting_visible_df=starting_df, starting_metadata=DataFrame())
        assert_frame_equal(result_df, DataFrame({
            'Category': ['A', 'B', 'C'],
            'Message': ['LINE1', 'LINE2', 'LINE3']
        }))

        # DataColumn is always casted to string
        col_list = [DataColumn([1, 2, 3], name='Numbers')]
        result_df = LogsManager().simulate_rendered_data(col_list)
        assert_frame_equal(result_df, DataFrame({
            'Numbers': ['1', '2', '3']
        }))



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
            'Collapsing Rows': [True, False, True, False, True]
        })
        col_list = [
            DataColumn(input_df['Message']),
            MetadataColumn(input_df['Category']),
            CollapsingRowsColumn(input_df['Collapsing Rows'])
        ]
        result_df = LogsManager().simulate_rendered_data(col_list)
        expected_df = DataFrame({
            'Message': ['line1', 'line3', 'line5']
        })
        assert_frame_equal(result_df, expected_df)

    

    def test_simulate_rendered_data_with_all_columns(self):
        # Test real-life scenario with all column types
        col_list = [
            CollapsingRowsColumn([False, True, False], name='Show Failed Only', collapse_heading_pattern="<Collapsed>"),
            DataColumn(['Sender1', 'Sender2', 'Sender3'], name='From'),
            DataColumn(['Receiver1', 'Receiver2', 'Receiver3'], name='To'),
            DataColumn(['Success', 'Failed', 'Success'], name='Category'),
            DataColumn(['Random Message1', 'Random Message2', 'Random Message3'], name='Message'),
            MetadataColumn(['TCP', 'UDP', 'TCP'], name='Protocol', category='Network')
        ]

        result_df = LogsManager().simulate_rendered_data(col_list)
        expected_df = DataFrame({
            'From': ['Sender2'],
            'To': ['Receiver2'],
            'Category': ['Failed']
        })
        print(result_df)
        assert_frame_equal(result_df, expected_df)
    


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
            DataColumn(input_df['Message']),
            MetadataColumn(input_df['Level'])
        ])
        visible_df, metadata_df = LogsManager().get_data(), LogsManager().get_metadata()
        assert_frame_equal(visible_df, DataFrame({
            'Message': ['line1', 'line2', 'line3']
        }))
        assert_frame_equal(metadata_df, DataFrame({
            'Level': ['info', 'error', 'debug']
        }))

        # Add more columns
        LogsManager().add_new_columns([
            DataColumn(['A', 'B', 'C'], name='Category')
        ])
        visible_df, metadata_df = LogsManager().get_data(), LogsManager().get_metadata()
        assert_frame_equal(visible_df, DataFrame({
            'Message': ['line1', 'line2', 'line3'],
            'Category': ['A', 'B', 'C']
        }))
        assert_frame_equal(metadata_df, DataFrame({
            'Level': ['info', 'error', 'debug']
        }))

        # Modify existing column
        LogsManager().add_new_columns([
            DataColumn(input_df['Message'].str.upper(), name='Message')
        ])
        visible_df, metadata_df = LogsManager().get_data(), LogsManager().get_metadata()
        assert_frame_equal(visible_df, DataFrame({
            'Category': ['A', 'B', 'C'],
            'Message': ['LINE1', 'LINE2', 'LINE3'],
        }))
        assert_frame_equal(metadata_df, DataFrame({
            'Level': ['info', 'error', 'debug']
        }))

        # Collapse rows
        LogsManager().add_new_columns([
            CollapsingRowsColumn([False, True, False], name='Show Failed Only')
        ])
        visible_df, metadata_df = LogsManager().get_data(), LogsManager().get_metadata()
        assert_frame_equal(visible_df, DataFrame({
            'Category': ['B'],
            'Message': ['LINE2'],
        }))
        assert_frame_equal(metadata_df, DataFrame({
            'Level': ['error']
        }))
        # Check if without collapsing we still cached the data correctly
        visible_df, metadata_df = LogsManager().get_data(show_collapsed=False)
        assert_frame_equal(visible_df, DataFrame({
            'Category': ['A', 'B', 'C'],
            'Message': ['LINE1', 'LINE2', 'LINE3']
        }))
        assert_frame_equal(metadata_df, DataFrame({
            'Level': ['info', 'error', 'debug']
        }))
