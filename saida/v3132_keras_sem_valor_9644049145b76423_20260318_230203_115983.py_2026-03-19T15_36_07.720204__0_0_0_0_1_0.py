def _build_attention(self, rank):
    """Builds multi-head dot-product attention computations.

        This function builds attributes necessary for `_compute_attention` to
        customize attention computation to replace the default dot-product
        attention.

        Args:
            rank: the rank of query, key, value tensors.
        """
    if self._attention_axes is None:
        self._attention_axes = tuple(range(1, rank - 2))
    else:
        self._attention_axes = tuple((axis if axis >= 0 else rank - 1 + axis for axis in self._attention_axes))
    (self._dot_product_equation, self._combine_equation, attn_scores_rank) = _build_attention_equation(rank, attn_axes=self._attention_axes)
    norm_axes = tuple(range(attn_scores_rank - len(self._attention_axes), attn_scores_rank))
    self._softmax = Softmax(axis=norm_axes, dtype=self.dtype_policy)
    self._dropout_layer = Dropout(rate=self._dropout, dtype=self.dtype_policy, seed=self.seed)