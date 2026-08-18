def __init__(self, num_classes, name=None, dtype=None, ignore_class=None, sparse_y_true=True, sparse_y_pred=True, axis=-1):
    target_class_ids = list(range(num_classes))
    super().__init__(name=name, num_classes=num_classes, target_class_ids=target_class_ids, axis=axis, dtype=dtype, ignore_class=ignore_class, sparse_y_true=sparse_y_true, sparse_y_pred=sparse_y_pred)