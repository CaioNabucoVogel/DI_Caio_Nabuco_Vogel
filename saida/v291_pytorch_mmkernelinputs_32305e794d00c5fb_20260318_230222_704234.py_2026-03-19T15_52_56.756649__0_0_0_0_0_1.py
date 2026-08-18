def __init__(self, input_nodes: list[Any], scalars: Optional[dict[str, Union[float, int]]]=None, out_dtype: Optional[torch.dtype]=None, mat1_idx: int=-2, mat2_idx: int=-1):
    """
        Initialize with a tuple of input nodes.

        By default, we assume the last 2 input nodes are mat1 and mat2, but
        the caller can adjust when necessary
        """
    super().__init__(input_nodes, scalars, out_dtype)
    assert len(self._input_nodes) >= 2, 'Expected at least 2 input nodes'
    (m1_idx, m2_idx) = (mat1_idx, mat2_idx)
    if mat1_idx < 0:
        m1_idx += len(input_nodes)
    if mat2_idx < 0:
        m2_idx += len(input_nodes)
    assert 0 <= m1_idx < len(input_nodes), f'Invalid mat1_idx: {mat1_idx}'
    assert 0 <= m2_idx < len(input_nodes), f'Invalid mat2_idx: {mat2_idx}'
    self._mat1_idx = mat1_idx
    self._mat2_idx = mat2_idx