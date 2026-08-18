def set_dirty(item, dirty):
    if dirty or not hasattr(item, '_v_signature'):
        item._v_signature = None