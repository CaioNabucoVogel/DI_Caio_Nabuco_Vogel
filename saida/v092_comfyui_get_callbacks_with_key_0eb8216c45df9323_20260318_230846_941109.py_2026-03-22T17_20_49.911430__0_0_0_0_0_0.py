def get_callbacks_with_key(call_type: str, key: str, transformer_options: dict, is_model_options=False):
    if is_model_options:
        transformer_options = transformer_options.get('transformer_options', {})
    c_list = []
    callbacks: dict[str, list] = transformer_options.get('callbacks', {})
    c_list.extend(callbacks.get(call_type, {}).get(key, []))
    return c_list