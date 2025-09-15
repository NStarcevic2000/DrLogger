from util.generate_namespace import get_namespaces

RESERVED_COLUMN_NAMES = get_namespaces({
    "File": "File",
    "Message": "Message",
    "Timestamp": "Timestamp"
}, str)

RESERVED_METADATA_NAMES = get_namespaces({
    "General": {
        "ForegroundColor": "#000000",
        "BackgroundColor": "#FFFFFF",
        "FontStyle": "Normal"
    }
}, str)