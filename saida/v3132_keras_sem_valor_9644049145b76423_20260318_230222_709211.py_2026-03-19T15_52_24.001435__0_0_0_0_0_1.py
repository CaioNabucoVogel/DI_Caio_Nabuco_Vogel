def test_class_weight(self):
    x = np.random.randint(1, 100, (4, 5))
    y = np.array([0, 1, 2, 1])
    class_w = {0: 2, 1: 1, 2: 3}
    py_dataset = ExamplePyDataset(x, y, batch_size=2)
    adapter = py_dataset_adapter.PyDatasetAdapter(py_dataset, shuffle=False, class_weight=class_w)
    if backend.backend() == 'tensorflow':
        gen = adapter.get_tf_dataset()
    elif backend.backend() == 'jax':
        gen = adapter.get_jax_iterator()
    elif backend.backend() == 'torch':
        gen = adapter.get_torch_dataloader()
    else:
        gen = adapter.get_numpy_iterator()
    for (index, batch) in enumerate(gen):
        self.assertLen(batch, 3)
        batch = [backend.convert_to_numpy(x) for x in batch]
        for sub_elem in range(2):
            self.assertAllEqual(batch[0][sub_elem], x[index * 2 + sub_elem])
            self.assertEqual(batch[1][sub_elem], y[index * 2 + sub_elem])
            class_key = np.int32(batch[1][sub_elem])
            self.assertEqual(batch[2][sub_elem], class_w[class_key])
    self.assertEqual(index, 1)