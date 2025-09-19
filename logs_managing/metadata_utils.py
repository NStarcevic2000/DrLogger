from pandas import Series, DataFrame

from logs_managing.reserved_names import RESERVED_METADATA_NAMES as RMetaNS

def get_style_from_metadata(metadata: Series, rows:int|list[int]|None=None) -> dict|Series:
    ''' Get style dictionary from metadata for a specific row.
        @param metadata: Series of dicts with metadata
        @param row: Row index to get style for
    '''
    if metadata is None or metadata.empty:
        return (None, None)
    elif rows is None:
        return (
            metadata[RMetaNS.General.name][RMetaNS.General.ForegroundColor],
            metadata[RMetaNS.General.name][RMetaNS.General.BackgroundColor]
        )
    elif isinstance(rows, int):
        return (
            metadata.loc[[rows]].iloc[0][RMetaNS.General.name][RMetaNS.General.ForegroundColor],
            metadata.loc[[rows]].iloc[0][RMetaNS.General.name][RMetaNS.General.BackgroundColor]
        )
    elif isinstance(rows, list):
        ret = [(
            metadata.loc[[row]].iloc[0][RMetaNS.General.name][RMetaNS.General.ForegroundColor],
            metadata.loc[[row]].iloc[0][RMetaNS.General.name][RMetaNS.General.BackgroundColor]
        ) for row in rows]
        return ret
    return (None, None)