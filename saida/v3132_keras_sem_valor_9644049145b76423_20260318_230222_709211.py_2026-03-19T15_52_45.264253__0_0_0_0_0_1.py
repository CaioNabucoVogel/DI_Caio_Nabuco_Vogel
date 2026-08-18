def test_iterate_infinite_with_none_num_batches(self):
    py_dataset = ExamplePyDataset(np.ones((6, 11), dtype='int32'), np.zeros((6, 11), dtype='int32'), batch_size=2, infinite=True)
    for (index, _) in enumerate(py_dataset):
        if index >= 10:
            break