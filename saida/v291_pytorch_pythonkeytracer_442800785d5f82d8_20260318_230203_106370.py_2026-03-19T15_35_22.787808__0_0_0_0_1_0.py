def create_node(self, kind: str, target: Target, args: tuple[Argument, ...], kwargs: dict[str, Argument], name: Optional[str]=None, type_expr: Optional[Any]=None) -> torch.fx.Node:
    node = super().create_node(kind, target, args, kwargs, name, type_expr)
    if node.op in ['placeholder', 'output'] and 'stack_trace' in node.meta:
        del node.meta['stack_trace']
    if kind == 'get_attr':
        assert isinstance(target, str)
        attr = getattr(self.root, target)
        if isinstance(attr, torch.Tensor):
            with disable_proxy_modes_tracing():
                node.meta['val'] = extract_val(attr)

    def map_fn(v: Any) -> Optional[_ExtractValType]:
        if not isinstance(v, torch.fx.Node) or 'val' not in v.meta:
            return None
        val = v.meta['val']
        if isinstance(val, torch.Tensor) and (not isinstance(val, FakeTensor)):
            return None
        return extract_val(v.meta['val'])
    if _should_save_eager_input_vals(target, (args, kwargs)):
        (arg_inp, kwarg_inp) = torch.fx.node.map_aggregate((args, kwargs), map_fn)
        node.meta['eager_input_vals'] = (arg_inp, kwarg_inp)
    return node