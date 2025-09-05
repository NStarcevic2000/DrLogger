from enum import Enum

class KEEP_SOURCE_FILE_LOCATION_ENUM(Enum):
    NONE = "None"
    FILE_ONLY = "File only"
    SHORT_PATH = "Short Path"
    FULL_PATH = "Full Path"
    def get_values(): return [e.value for e in KEEP_SOURCE_FILE_LOCATION_ENUM]

class CONTEXTUALIZE_LINES_ENUM(Enum):
    NONE = "None"
    LINES_BEFORE = "Lines before"
    LINES_AFTER = "Lines after"
    LINES_BEFORE_AND_AFTER = "Lines before and after"
    def get_values(): return [e.value for e in CONTEXTUALIZE_LINES_ENUM]