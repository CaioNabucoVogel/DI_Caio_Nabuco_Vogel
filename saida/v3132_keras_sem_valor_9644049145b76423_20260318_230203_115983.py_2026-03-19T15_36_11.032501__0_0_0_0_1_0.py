def call(self, query, value, key=None, query_mask=None, value_mask=None, key_mask=None, attention_mask=None, return_attention_scores=False, training=None, use_causal_mask=False):
    if key is None:
        key = value
    query_mask = backend.get_keras_mask(query)
    backend.set_keras_mask(query, None)
    backend.set_keras_mask(value, None)
    backend.set_keras_mask(key, None)
    attention_mask = self._compute_attention_mask(query, value, query_mask=query_mask, value_mask=value_mask, key_mask=key_mask, attention_mask=attention_mask, use_causal_mask=use_causal_mask)
    query = self._query_dense(query)
    key = self._key_dense(key)
    value = self._value_dense(value)
    (attention_output, attention_scores) = self._compute_attention(query, key, value, attention_mask, training, return_attention_scores)
    attention_output = self._output_dense(attention_output)
    if query_mask is not None:
        backend.set_keras_mask(attention_output, query_mask)
    if return_attention_scores:
        return (attention_output, attention_scores)
    return attention_output