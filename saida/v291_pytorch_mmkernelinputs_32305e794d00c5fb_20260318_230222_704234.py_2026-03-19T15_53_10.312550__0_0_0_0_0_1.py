def mnk_hinted(self) -> tuple[int, int, int]:
    """
        Get the hinted M, N, K dimensions for matrix multiplication.
        Handles both 2D (MM) and 3D (BMM) tensors.

        Uses shapes_hinted from the base class to get integer hints for dimensions.

        Returns:
            A tuple of (M, N, K) dimensions as integers
        """
    hinted_shapes = self.shapes_hinted()
    mat1_shape = hinted_shapes[self._mat1_idx]
    mat2_shape = hinted_shapes[self._mat2_idx]
    m = mat1_shape[-2]
    k = mat1_shape[-1]
    n = mat2_shape[-1]
    k_check = mat2_shape[-2]
    assert k == k_check, f"K dimensions don't match: {k} vs {k_check}"
    return (m, n, k)