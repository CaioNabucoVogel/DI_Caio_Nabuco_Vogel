def __init__(self, from_logits=False, ignore_class=None, reduction='sum_over_batch_size', axis=-1, name='sparse_categorical_crossentropy', dtype=None):
    super().__init__(sparse_categorical_crossentropy, name=name, reduction=reduction, dtype=dtype, from_logits=from_logits, ignore_class=ignore_class, axis=axis)
    self.from_logits = from_logits
    self.ignore_class = ignore_class