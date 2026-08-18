def _param(account_id: str, region_name: str, params, logical_resource_id, *args, **kwargs):
    tags = params.get('Tags')
    if not tags:
        return None
    return [{'ResourceType': resource_type, 'Tags': tags}]
    return _param