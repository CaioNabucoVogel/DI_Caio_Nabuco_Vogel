def _compute_attention(self, query, key, value, attention_mask=None, training=None, return_attention_scores=False):
    """Applies Dot-product attention with query, key, value tensors.

        This function defines the computation inside `call` with projected
        multi-head Q, K, V inputs. Users can override this function for
        customized attention implementation.

        Args:
            query: Projected query tensor of shape `(B, T, N, key_dim)`.
            key: Projected key tensor of shape `(B, S, N, key_dim)`.
            value: Projected value tensor of shape `(B, S, N, value_dim)`.
            attention_mask: a boolean mask of shape `(B, T, S)`, that prevents
                attention to certain positions. It is generally not needed if
                the `query` and `value` (and/or `key`) are masked.
            training: Python boolean indicating whether the layer should behave
                in training mode (adding dropout) or in inference mode (doing
                nothing).

        Returns:
          attention_output: Multi-headed outputs of attention computation.
          attention_scores: Multi-headed attention weights.
        """
    if self._flash_attention and return_attention_scores:
        raise ValueError('Returning attention scores is not supported when flash attention is enabled. Please disable flash attention to access attention scores.')
    use_dot_product_attention = not (self._dropout > 0.0 or return_attention_scores or len(query.shape) != 4)
    if use_dot_product_attention:
        if attention_mask is not None:
            mask_expansion_axis = -len(self._attention_axes) * 2 - 1
            len_attention_scores_shape = 4
            for _ in range(len_attention_scores_shape - len(attention_mask.shape)):
                attention_mask = ops.expand_dims(attention_mask, axis=mask_expansion_axis)
            attention_mask = ops.cast(attention_mask, dtype='bool')
        attention_output = ops.dot_product_attention(query=query, key=key, value=value, bias=None, mask=attention_mask, scale=self._inverse_sqrt_key_dim, is_causal=False, flash_attention=self._flash_attention)
        return (attention_output, None)
    query = ops.multiply(query, ops.cast(self._inverse_sqrt_key_dim, query.dtype))
    attention_scores = ops.einsum(self._dot_product_equation, key, query)
    attention_scores = self._masked_softmax(attention_scores, attention_mask)
    if self._dropout > 0.0:
        final_attn_scores = self._dropout_layer(attention_scores, training=training)
    else:
        final_attn_scores = attention_scores
    attention_output = ops.einsum(self._combine_equation, final_attn_scores, value)
    return (attention_output, attention_scores)