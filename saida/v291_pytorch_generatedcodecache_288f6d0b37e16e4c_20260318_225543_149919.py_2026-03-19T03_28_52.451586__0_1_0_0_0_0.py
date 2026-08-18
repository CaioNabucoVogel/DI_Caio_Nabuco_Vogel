class GeneratedCodeCache:
    """
    Cache for generated code. The cache key is a string representation of the input nodes,
    number of stages, number of warps, and call sizes. The cache value is a tuple of the
    generated code, extra code, and events.
    """

    def __init__(self, *args, **kwargs):
        self._cache: dict[str, GeneratedCodeCacheEntry] = {}

    def cache_clear(self) -> None:
        self._cache.clear()

    def __repr__(self):
        return repr(self._cache)

    def make_key(self, input_nodes: tuple[ir.IRNode, ...], num_stages: int, num_warps: int, call_sizes: Sequence[sympy.core.symbol.Symbol], prefix_args: int, suffix_args: int, epilogue_fn: Optional[Callable[..., Any]], epilogue_fn_hash: Optional[str], tma_store: bool, transpose_discontiguous_tensor_descriptors_override: Optional[bool], subgraphs: Optional[list[ir.Buffer]], workspace_arg: Optional[WorkspaceArg], layout: ir.Layout, num_consumer_groups: int, num_buffers_warp_spec: int, kwargs: dict[str, Any], hint_override: Optional[int]=None) -> Optional[str]:

        def layout_key(layout: ir.Layout) -> str:
            assert not isinstance(layout, ir.FlexibleLayout)
            return repr([layout.size, layout.stride, layout.dtype, layout.device, layout.offset])

        def has_flexible_layout() -> bool:
            if isinstance(layout, ir.FlexibleLayout):
                return True
            for input in input_nodes:
                if isinstance(input.get_layout(), ir.FlexibleLayout):
                    return True
            return False
        if epilogue_fn is identity:
            assert epilogue_fn_hash is None
            epilogue_fn_hash = 'identity'
        if has_flexible_layout() or subgraphs is not None or workspace_arg is not None or (epilogue_fn_hash is None):
            return None
        return repr({'input_nodes': [layout_key(input.get_layout()) for input in input_nodes], 'num_stages': num_stages, 'num_warps': num_warps, 'prefix_args': prefix_args, 'suffix_args': suffix_args, 'call_sizes': call_sizes, 'layout': layout_key(layout), 'num_consumer_groups': num_consumer_groups, 'num_buffers_warp_spec': num_buffers_warp_spec, 'epilogue_fn_hash': epilogue_fn_hash, 'tma_store': tma_store, 'transpose_discontiguous_tensor_descriptors_override': transpose_discontiguous_tensor_descriptors_override, 'kwargs': kwargs, 'hint_override': hint_override})

    def get_entry(self, cache_key: Optional[str]) -> Optional[GeneratedCodeCacheEntry]:
        if cache_key is None:
            return None
        entry = self._cache.get(cache_key, None)
        if entry is None:
            torch._dynamo.utils.counters['inductor']['generated_module_cache_miss'] += 1
        else:
            torch._dynamo.utils.counters['inductor']['generated_module_cache_hit'] += 1
        return entry

    def put_entry(self, cache_key: Optional[str], code: str, extra: str, events: list[Any]) -> None:
        if cache_key is None:
            return
        entry = GeneratedCodeCacheEntry(code, extra, events)
        self._cache.update({cache_key: entry})