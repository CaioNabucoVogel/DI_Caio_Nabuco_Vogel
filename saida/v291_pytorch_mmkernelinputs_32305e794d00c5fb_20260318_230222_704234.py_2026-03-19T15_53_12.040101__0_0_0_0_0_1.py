def batch_hinted(self) -> int:
    """
        Get the hinted batch size for batched matrix multiplication.
        Returns 1 for non-batched (2D) operations.

        Returns:
            The batch size as an integer
        """
    hinted_shapes = self.shapes_hinted()
    mat1_shape = hinted_shapes[self._mat1_idx]
    if len(mat1_shape) >= 3:
        return mat1_shape[-3]
    return 1