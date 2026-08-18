def index_expr(cls, index: Any, dtype: torch.dtype) -> ValueRanges[Any]:
    assert isinstance(index, ValueRanges)
    return cls.to_dtype(index, dtype)