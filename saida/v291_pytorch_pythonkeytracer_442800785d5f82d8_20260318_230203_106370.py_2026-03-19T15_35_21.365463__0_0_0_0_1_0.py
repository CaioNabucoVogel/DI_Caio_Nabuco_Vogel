def unwrap_proxy(self, e: T) -> object:
    if isinstance(e, Tensor):
        return get_proxy_slot(e, self, e, lambda x: x.proxy)
    elif isinstance(e, py_sym_types):
        return get_proxy_slot(e, self, e, lambda e: e.force())
    elif isinstance(e, _AnyScriptObject) or is_opaque_value(e):
        return get_proxy_slot(e, self, e)
    else:
        return e