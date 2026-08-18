def compute_output_spec(self, query, value, key=None, query_mask=None, value_mask=None, key_mask=None, attention_mask=None, return_attention_scores=False, training=None, use_causal_mask=False):
    if key is not None:
        key_shape = key.shape
    else:
        key_shape = None
    output_shape = self.compute_output_shape(query.shape, value.shape, key_shape)
    output_spec = backend.KerasTensor(output_shape, dtype=self.compute_dtype)
    if return_attention_scores:
        length = query.shape[1]
        attention_shape = (query.shape[0], self.num_heads, length, length)
        return (output_spec, backend.KerasTensor(attention_shape, dtype=self.compute_dtype))
    return output_spec