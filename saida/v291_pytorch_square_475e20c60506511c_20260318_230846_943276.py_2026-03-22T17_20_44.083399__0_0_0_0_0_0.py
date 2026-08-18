def square(x: Any) -> ValueRanges[Any]:
    return ValueRanges.convex_min_zero_map(x, lambda y: PowByNatural(y, 2))