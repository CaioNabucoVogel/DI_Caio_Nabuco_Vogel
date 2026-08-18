def hard_shrink(x, threshold=0.5):
    """Hard Shrink activation function.

    The Hard Shrink function is a thresholding operation defined as:

    `f(x) = x` if `|x| > threshold`,
    `f(x) = 0` otherwise.

    Args:
        x: Input tensor.
        threshold: Threshold value. Defaults to 0.5.

    Returns:
        A tensor with the same shape as `x`.

    Example:

    >>> x = np.array([-0.5, 0., 1.])
    >>> x_hard_shrink = keras.ops.hard_shrink(x)
    >>> print(x_hard_shrink)
    array([0. 0. 1.], shape=(3,), dtype=float64)

    """
    if any_symbolic_tensors((x,)):
        return HardShrink(threshold).symbolic_call(x)
    return backend.nn.hard_shrink(x, threshold)