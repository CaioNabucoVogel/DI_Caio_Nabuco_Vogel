def stack_residual_blocks_v2(x, filters, blocks, stride1=2, name=None):
    """A set of stacked residual blocks.

    Args:
        x: Input tensor.
        filters: Number of filters in the bottleneck layer in a block.
        blocks: Number of blocks in the stacked blocks.
        stride1: Stride of the first layer in the first block. Defaults to `2`.
        name: Stack label.

    Returns:
        Output tensor for the stacked blocks.
    """
    x = residual_block_v2(x, filters, conv_shortcut=True, name=f'{name}_block1')
    for i in range(2, blocks):
        x = residual_block_v2(x, filters, name=f'{name}_block{i}')
    x = residual_block_v2(x, filters, stride=stride1, name=f'{name}_block{str(blocks)}')
    return x