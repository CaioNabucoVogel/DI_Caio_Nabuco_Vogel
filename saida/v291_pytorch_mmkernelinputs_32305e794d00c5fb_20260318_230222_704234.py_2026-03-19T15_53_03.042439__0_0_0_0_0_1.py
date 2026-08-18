def out_dtype(self) -> torch.dtype:
    """
        Get the output dtype, whether passed in or inferred from the nodes

        Returns:
            The output dtype
        """
    if self._out_dtype is not None:
        return self._out_dtype
    return self.mat1mat2()[0].get_dtype()