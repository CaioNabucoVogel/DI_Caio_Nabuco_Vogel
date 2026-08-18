def roundup(x: int, multiple: int) -> int:
    """Round up x to the nearest multiple."""
    return (x + multiple - 1) // multiple * multiple