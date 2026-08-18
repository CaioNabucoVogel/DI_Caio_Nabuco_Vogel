def mnk_symbolic(self) -> tuple[sympy.Integer, sympy.Integer, sympy.Integer]:
    """
        Get the symbolic M, N, K dimensions for matrix multiplication.
        Handles both 2D (MM) and 3D (BMM) tensors.

        M is extracted from the second-to-last dimension of the first operand (mat1).
        N is extracted from the last dimension of the second operand (mat2).
        K is extracted from the last dimension of the first operand (mat1).

        Returns:
            A tuple of (M, N, K) dimensions
        """
    mat1 = self.nodes()[self._mat1_idx]
    mat2 = self.nodes()[self._mat2_idx]
    m = mat1.get_size()[-2]
    k = mat1.get_size()[-1]
    n = mat2.get_size()[-1]
    k0 = mat2.get_size()[-2]
    V.graph.sizevars.check_equals(k, k0)
    return (m, n, k)