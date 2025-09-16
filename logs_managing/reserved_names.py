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
    },
    "CaptureRows": {
        "CaptureRows": "Collapsed Rows",
        "FromToIndexes": "From-To Indexes",
        "CollapsedInTotal": "Collapsed in Total"
    }
}, str)
print(RESERVED_METADATA_NAMES)