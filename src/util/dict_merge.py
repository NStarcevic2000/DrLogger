# Merge in depth two dictionaries
def merge_dicts(orig, new):
    if not isinstance(orig, dict) or not isinstance(new, dict):
        return new
    merged = orig.copy()
    for k, v in new.items():
        if k in merged:
            merged[k] = merge_dicts(merged[k], v)
        else:
            merged[k] = v
    return merged

# Overlay in depth two dictionaries (only right to left merging for keys existing in both dicts)
def overlay_dict(orig, overlay):
    if not isinstance(orig, dict) or not isinstance(overlay, dict):
        return orig
    result = orig.copy()
    for k, v in overlay.items():
        if k in result:
            if isinstance(result[k], dict) and isinstance(v, dict):
                result[k] = overlay_dict(result[k], v)
            else:
                result[k] = v
    return result
