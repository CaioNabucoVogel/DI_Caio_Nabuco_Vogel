def stochastic_round_quantize_nvfp4_by_block(x, per_tensor_scale, pad_16x, seed=0, block_size=4096 * 4096):

    def roundup(x: int, multiple: int) -> int:
        """Round up x to the nearest multiple."""
        return (x + multiple - 1) // multiple * multiple
    orig_shape = x.shape
    if pad_16x:
        (rows, cols) = x.shape
        padded_rows = roundup(rows, 16)
        padded_cols = roundup(cols, 16)
        if padded_rows != rows or padded_cols != cols:
            x = torch.nn.functional.pad(x, (0, padded_cols - cols, 0, padded_rows - rows))
            orig_shape = x.shape
    orig_shape = list(orig_shape)
    output_fp4 = torch.empty(orig_shape[:-1] + [orig_shape[-1] // 2], dtype=torch.uint8, device=x.device)
    output_block = torch.empty(orig_shape[:-1] + [orig_shape[-1] // 16], dtype=torch.float8_e4m3fn, device=x.device)
    generator = torch.Generator(device=x.device)
    generator.manual_seed(seed)
    num_slices = max(1, x.numel() / block_size)
    slice_size = max(1, round(x.shape[0] / num_slices))
    for i in range(0, x.shape[0], slice_size):
        (fp4, block) = stochastic_round_quantize_nvfp4_block(x[i:i + slice_size], per_tensor_scale, generator=generator)
        output_fp4[i:i + slice_size].copy_(fp4)
        output_block[i:i + slice_size].copy_(block)