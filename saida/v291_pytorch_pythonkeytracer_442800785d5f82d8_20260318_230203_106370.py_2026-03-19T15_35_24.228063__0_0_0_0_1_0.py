def map_fn(v: Any) -> Optional[_ExtractValType]:
    if not isinstance(v, torch.fx.Node) or 'val' not in v.meta:
        return None
    val = v.meta['val']
    if isinstance(val, torch.Tensor) and (not isinstance(val, FakeTensor)):
        return None
    return extract_val(v.meta['val'])