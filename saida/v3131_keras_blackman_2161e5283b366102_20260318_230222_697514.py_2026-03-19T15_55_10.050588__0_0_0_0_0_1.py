def blackman(x):
    dtype = config.floatx()
    x = tf.cast(x, dtype)
    n = tf.range(x, dtype=dtype)
    n_minus_1 = tf.cast(x - 1, dtype)
    term1 = 0.42
    term2 = -0.5 * tf.cos(2 * np.pi * n / n_minus_1)
    term3 = 0.08 * tf.cos(4 * np.pi * n / n_minus_1)
    window = term1 + term2 + term3
    return window