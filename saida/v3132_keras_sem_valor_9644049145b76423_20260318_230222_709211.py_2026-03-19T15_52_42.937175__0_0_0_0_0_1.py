def test_iterate_finite(self):
    py_dataset = ExamplePyDataset(np.ones((6, 11), dtype='int32'), np.zeros((6, 11), dtype='int32'), batch_size=2)
    batches = [batch for batch in py_dataset]
    self.assertLen(batches, 3)