def uniform(shape, minval=0.0, maxval=1.0, dtype=None, seed=None):
    dtype = dtype or floatx()
    seed = draw_seed(seed)
    rng = np.random.default_rng(seed)
    return rng.uniform(size=shape, low=minval, high=maxval).astype(dtype)