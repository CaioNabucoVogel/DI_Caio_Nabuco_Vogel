@classmethod
def _get_uncompiled_header(cls, device: str) -> str | None:
    """Header precompiling is currently disabled for halide."""
    return None