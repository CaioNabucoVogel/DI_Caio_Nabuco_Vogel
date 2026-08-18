def _compute_causal_mask(self, query, value=None):
    """Computes a causal mask (e.g., for masked self-attention layers).

        For example, if query and value both contain sequences of length 4,
        this function returns a boolean tensor equal to:

        ```
        [[[True,  False, False, False],
          [True,  True,  False, False],
          [True,  True,  True,  False],
          [True,  True,  True,  True]]]
        ```

        Args:
            query: query tensor of shape `(B, T, ...)`.
            value: value tensor of shape `(B, S, ...)` (optional, defaults to
                query).

        Returns:
            mask: a boolean tensor of shape `(1, T, S)` containing a lower
                triangular matrix of shape `(T, S)`.
        """
    q_seq_length = ops.shape(query)[1]
    v_seq_length = q_seq_length if value is None else ops.shape(value)[1]
    ones_mask = ops.ones((1, q_seq_length, v_seq_length), dtype='int32')
    row_index = ops.cumsum(ones_mask, axis=-2)
    col_index = ops.cumsum(ones_mask, axis=-1)
    return ops.greater_equal(row_index, col_index)