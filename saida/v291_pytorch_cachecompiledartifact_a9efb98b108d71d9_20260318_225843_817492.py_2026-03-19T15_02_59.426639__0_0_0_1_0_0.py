def __init__(self, compiled_fn: Callable[..., Any], artifacts: Optional[tuple[bytes, CacheInfo]]):
    self._compiled_fn = compiled_fn
    self._artifacts = artifacts