def get_wrappers_with_key(wrapper_type: str, key: str, transformer_options: dict, is_model_options=False):
    if is_model_options:
        transformer_options = transformer_options.get('transformer_options', {})
    w_list = []
    wrappers: dict[str, list] = transformer_options.get('wrappers', {})
    w_list.extend(wrappers.get(wrapper_type, {}).get(key, []))
    return w_list