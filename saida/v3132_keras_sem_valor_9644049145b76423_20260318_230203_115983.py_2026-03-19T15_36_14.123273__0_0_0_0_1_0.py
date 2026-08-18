def compute_output_shape(self, query_shape, value_shape, key_shape=None):
    query_shape = tuple(query_shape)
    value_shape = tuple(value_shape)
    if key_shape is None:
        key_shape = value_shape
    else:
        key_shape = tuple(key_shape)
    if value_shape[1:-1] != key_shape[1:-1]:
        raise ValueError(f'All dimensions of `value` and `key`, except the last one, must be equal. Received: value_shape={value_shape} and key_shape={key_shape}')
    if self._output_shape:
        query_shape = query_shape[:-1] + self._output_shape
    return query_shape