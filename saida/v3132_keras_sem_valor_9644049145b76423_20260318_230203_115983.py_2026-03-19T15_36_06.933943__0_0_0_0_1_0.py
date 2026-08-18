def _make_output_dense(self, query_shape, common_kwargs, name=None):
    """Builds the output projection matrix.

        Args:
            free_dims: Number of free dimensions for einsum equation building.
            common_kwargs: Common keyword arguments for einsum layer.
            name: Name for the projection layer.

        Returns:
            Projection layer.
        """
    query_rank = len(query_shape)
    if self._output_shape:
        output_shape = self._output_shape
    else:
        output_shape = [query_shape[-1]]
    (einsum_equation, bias_axes, output_rank) = _build_proj_equation(query_rank - 1, bound_dims=2, output_dims=len(output_shape))
    return EinsumDense(einsum_equation, output_shape=_get_output_shape(output_rank - 1, output_shape), bias_axes=bias_axes if self._use_bias else None, name=name, **common_kwargs)