def __init__(self, q=0.5, reduction='sum_over_batch_size', name='categorical_generalized_cross_entropy', dtype=None):
    if not 0 < q < 1:
        raise ValueError('q must be in the interval (0, 1)')
    super().__init__(categorical_generalized_cross_entropy, name=name, reduction=reduction, dtype=dtype, q=q)
    self.q = q