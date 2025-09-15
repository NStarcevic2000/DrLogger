# Merge in depth two dictionaries
def merge_dicts(orig, new):
    if not isinstance(orig, dict) or not isinstance(new, dict):
        return new
    for k, v in new.items():
        if k in orig:
            orig[k] = merge_dicts(orig[k], v)
        else:
            orig[k] = v
    return orig

# Overlay in depth two dictionaries (only right to left merging for keys existing in both dicts)
def overlay_dict(orig, overlay):
    if not isinstance(orig, dict) or not isinstance(overlay, dict):
        return overlay
    for k, v in overlay.items():
        if k in orig:
            orig[k] = overlay_dict(orig[k], v)
        else:
            orig[k] = v
    return orig
