def stochastic_round_quantize_nvfp4(x, per_tensor_scale, pad_16x, seed=0):

    def roundup(x: int, multiple: int) -> int:
        """Round up x to the nearest multiple."""
        return (x + multiple - 1) // multiple * multiple
    generator = torch.Generator(device=x.device)
    generator.manual_seed(seed)
    if pad_16x:
        (rows, cols) = x.shape
        padded_rows = roundup(rows, 16)
        padded_cols = roundup(cols, 16)
        if padded_rows != rows or padded_cols != cols:
            x = torch.nn.functional.pad(x, (0, padded_cols - cols, 0, padded_rows - rows))
    (x, blocked_scaled) = stochastic_round_quantize_nvfp4_block(x, per_tensor_scale, generator)
    return (x, to_blocked(blocked_scaled, flatten=False))