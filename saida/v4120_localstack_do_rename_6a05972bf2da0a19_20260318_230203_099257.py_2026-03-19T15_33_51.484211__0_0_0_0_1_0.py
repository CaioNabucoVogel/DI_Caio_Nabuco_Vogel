def do_rename(account_id, region_name, params, logical_resource_id, *args, **kwargs):
    values = func(account_id, region_name, params, logical_resource_id, *args, **kwargs) if func else params
    for (old_param, new_param) in rename_map.items():
        values[new_param] = values.pop(old_param, None)
    return values
    return do_rename