@staticmethod
def _generate_kernel_inputs_key(kernel_inputs: KernelInputs) -> str:
    """
        Generate a key based on input node properties and scalars.
        The key includes dtype, size, and stride information for each input node,
        plus scalar values as key=value pairs separated by & signs.
        """
    dtypes = kernel_inputs.dtypes()
    shapes = kernel_inputs.shapes_hinted()
    strides = kernel_inputs.strides_hinted()
    node_info = tuple(((dtype, list(shape), list(stride)) for (dtype, shape, stride) in zip(dtypes, shapes, strides)))
    fmt_key = str(node_info)
    if kernel_inputs._scalars:
        scalar_parts = [f'{key}={value}' for (key, value) in sorted(kernel_inputs._scalars.items())]
        scalars_key = '&'.join(scalar_parts)
        fmt_key = f'{fmt_key}+{scalars_key}'
    return f'{fmt_key}'