def test_with_different_shapes(self):

    class TestPyDataset(py_dataset_adapter.PyDataset):

        @property
        def num_batches(self):
            return 3

        def __getitem__(self, idx):
            if idx == 0:
                return (np.ones([16, 4], 'float32'), np.ones([16, 2], 'float32'))
            if idx == 1:
                return (np.ones([16, 5], 'float32'), np.ones([16, 2], 'float32'))
            else:
                return (np.ones([2, 6], 'float32'), np.ones([2, 2], 'float32'))
    adapter = py_dataset_adapter.PyDatasetAdapter(TestPyDataset(), shuffle=False)
    if backend.backend() == 'tensorflow':
        it = adapter.get_tf_dataset()
    elif backend.backend() == 'jax':
        it = adapter.get_jax_iterator()
    elif backend.backend() == 'torch':
        it = adapter.get_torch_dataloader()
    else:
        it = adapter.get_numpy_iterator()
    for (i, batch) in enumerate(it):
        self.assertEqual(len(batch), 2)
        (bx, by) = batch
        self.assertEqual(bx.dtype, by.dtype)
        self.assertContainsExactSubsequence(str(bx.dtype), 'float32')
        if i == 0:
            self.assertEqual(bx.shape, (16, 4))
            self.assertEqual(by.shape, (16, 2))
        elif i == 1:
            self.assertEqual(bx.shape, (16, 5))
            self.assertEqual(by.shape, (16, 2))
        else:
            self.assertEqual(bx.shape, (2, 6))
            self.assertEqual(by.shape, (2, 2))