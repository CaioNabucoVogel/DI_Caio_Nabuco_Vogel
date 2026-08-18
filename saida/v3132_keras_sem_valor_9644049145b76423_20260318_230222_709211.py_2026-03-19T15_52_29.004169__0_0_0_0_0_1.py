def test_dict_inputs(self):
    inputs = {'x': np.random.random((40, 4)), 'y': np.random.random((40, 2))}
    py_dataset = DictPyDataset(inputs, batch_size=4)
    adapter = py_dataset_adapter.PyDatasetAdapter(py_dataset, shuffle=False)
    gen = adapter.get_numpy_iterator()
    for batch in gen:
        self.assertEqual(len(batch), 2)
        (bx, by) = (batch['x'], batch['y'])
        self.assertIsInstance(bx, np.ndarray)
        self.assertIsInstance(by, np.ndarray)
        self.assertEqual(bx.dtype, by.dtype)
        self.assertEqual(bx.shape, (4, 4))
        self.assertEqual(by.shape, (4, 2))
    ds = adapter.get_tf_dataset()
    for batch in ds:
        self.assertEqual(len(batch), 2)
        (bx, by) = (batch['x'], batch['y'])
        self.assertIsInstance(bx, tf.Tensor)
        self.assertIsInstance(by, tf.Tensor)
        self.assertEqual(bx.dtype, by.dtype)
        self.assertEqual(tuple(bx.shape), (4, 4))
        self.assertEqual(tuple(by.shape), (4, 2))