def set_indirect(self, old: Expr, new: ValueRanges[Expr]) -> ValueRanges[Expr]:
    assert isinstance(new, ValueRanges)
    self.replacement_vals[old] = new
    return new