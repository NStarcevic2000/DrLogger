from pandas import Series, DataFrame

def get_style_from_metadata(metadata: Series, row: int) -> dict:
    ''' Get style dictionary from metadata for a specific row.
        @param metadata: Series with metadata
        @param row: Row index to get style for
        @return: Dictionary with style information
    '''
    if metadata is None or metadata.empty or row >= len(metadata):
        return {}
    style_info = metadata.iloc[row]
    if not isinstance(style_info, dict):
        return {}
    return style_info