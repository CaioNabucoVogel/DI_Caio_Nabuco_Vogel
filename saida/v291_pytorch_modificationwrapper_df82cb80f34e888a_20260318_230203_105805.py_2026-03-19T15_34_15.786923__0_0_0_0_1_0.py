def store(self, name: str, index: sympy.Expr, value: CSEVariable, mode: StoreMode=None) -> str:
    """Currently only supports stores for atomic adds coming from scatter nodes
        This is used by flex_attention's backwards grad for captured buffers, see
        zeros_and_scatter lowering
        """
    assert self.mask is not None, 'Mask is required for inner stores in modifications'
    assert mode == 'atomic_add', 'Only atomic_add is supported for inner stores'
    buf_name = self._add_kernel_input(name)
    index_str = self._process_indexing(index)
    index_str = f'tl.broadcast_to({index_str}, {value}.shape)'
    store = f"tl.atomic_add({buf_name} + {index_str}, {value}, {self.mask}, sem='relaxed')"
    return store