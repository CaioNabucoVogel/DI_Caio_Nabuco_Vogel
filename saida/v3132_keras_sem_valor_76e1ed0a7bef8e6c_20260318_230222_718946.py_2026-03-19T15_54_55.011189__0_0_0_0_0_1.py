def _get_indices(method):
    """Get values of y at the indices implied by method."""
    if method == 'lower':
        indices = tf.math.floor((d - 1) * q)
    elif method == 'higher':
        indices = tf.math.ceil((d - 1) * q)
    elif method == 'nearest':
        indices = tf.round((d - 1) * q)
    return tf.clip_by_value(tf.cast(indices, 'int32'), 0, tf.shape(y)[-1] - 1)