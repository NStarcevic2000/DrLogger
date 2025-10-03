from util.generate_namespace import get_namespaces

RESERVED_COLUMN_NAMES = get_namespaces({
    "File": "File",
    "Message": "Message",
    "Timestamp": "Timestamp"
}, str)

RESERVED_METADATA_NAMES = get_namespaces({
    "General": {
        "OriginalLogs": "Original Logs",
        "ForegroundColor": "Foreground Color",
        "BackgroundColor": "Background Color"
    },
    "Capture Rows": {
        "CaptureRows": "Captured Logs",
        "FromToIndexes": "From-To Indexes",
        "CollapsedInTotal": "Collapsed in Total"
    }
}, str)