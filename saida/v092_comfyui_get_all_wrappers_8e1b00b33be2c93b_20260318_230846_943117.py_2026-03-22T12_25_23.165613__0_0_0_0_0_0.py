def get_all_wrappers(wrapper_type: str, transformer_options: dict, is_model_options=False):
    if is_model_options:
        transformer_options = transformer_options.get('transformer_options', {})
    w_list = []
    wrappers: dict[str, list] = transformer_options.get('wrappers', {})
    for w in wrappers.get(wrapper_type, {}).values():
        w_list.extend(w)
    return w_list