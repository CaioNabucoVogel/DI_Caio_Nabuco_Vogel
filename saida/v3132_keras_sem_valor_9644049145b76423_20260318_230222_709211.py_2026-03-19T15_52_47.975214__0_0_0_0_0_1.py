def test_iterate_infinite_with_no_len(self):

    class NoLenDataset(py_dataset_adapter.PyDataset):

        def __getitem__(self, idx):
            yield np.ones((2, 11), dtype='int32')
    for (index, _) in enumerate(NoLenDataset()):
        if index >= 10:
            break