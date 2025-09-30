from logs_managing.logs_column_types import COLUMN_TYPE

def assert_columns_by_type(columns:list[COLUMN_TYPE], expected_types:list[tuple[COLUMN_TYPE, str]]):
    if isinstance(columns, COLUMN_TYPE):
        columns = [columns]
    elif not isinstance(columns, list) or not all(isinstance(x, COLUMN_TYPE) for x in columns):
        raise ValueError(f"Columns must be a COLUMN_TYPE or list of COLUMN_TYPE. Current value: {columns}")
    for i, (col, (col_type, col_name)) in enumerate(zip(columns, expected_types)):
        if not (isinstance(col, col_type) and getattr(col, 'name', None) == col_name):
            try:
                print(f"Debug: Failed at index {i}: got type {type(col)}, expected {col_type}; got name '{getattr(col, 'name', 'AttributeError')}', expected '{col_name}'")
            except Exception as e:
                print(f"Debug: Failed at index {i}: Error printing debug info: {e}. col={col}, col_type={col_type}, col_name={col_name}")
            assert False, f"Column at index {i} = (<{type(col)}>, '{getattr(col, 'name', 'AttributeError')}') does not match expected type \"<{col_type}>\" or name \"{col_name}\""