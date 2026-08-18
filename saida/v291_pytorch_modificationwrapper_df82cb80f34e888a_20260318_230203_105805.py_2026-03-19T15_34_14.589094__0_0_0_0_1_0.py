def indirect_indexing(self, index_var: str, size, check, wrap_neg=True):
    """Convert index variable to symbolic form."""
    return sympy_index_symbol(str(index_var))