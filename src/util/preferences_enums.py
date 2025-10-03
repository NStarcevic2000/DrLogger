from enum import Enum

class PREFERENCES_UI_THEME_ENUM(Enum):
    LIGHT = "Light"
    DARK = "Dark"
    def get_values(): return [e.value for e in PREFERENCES_UI_THEME_ENUM]