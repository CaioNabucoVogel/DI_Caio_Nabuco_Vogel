@parameterized.named_parameters([{'testcase_name': 'multiprocessing', 'workers': 2, 'use_multiprocessing': True, 'max_queue_size': 10}, {'testcase_name': 'multithreading', 'workers': 2, 'max_queue_size': 10}, {'testcase_name': 'single'}])
def test_exception_reported(self, workers=0, use_multiprocessing=False, max_queue_size=0):
    if backend.backend() == 'jax' and use_multiprocessing is True:
        self.skipTest('The CI failed for an unknown reason with `use_multiprocessing=True` in the jax backend')
    dataset = ExceptionPyDataset(workers=workers, use_multiprocessing=use_multiprocessing, max_queue_size=max_queue_size)
    adapter = py_dataset_adapter.PyDatasetAdapter(dataset, shuffle=False)
    expected_exception_class = ValueError
    if backend.backend() == 'tensorflow':
        it = adapter.get_tf_dataset()
        expected_exception_class = tf.errors.InvalidArgumentError
    elif backend.backend() == 'jax':
        it = adapter.get_jax_iterator()
    elif backend.backend() == 'torch':
        it = adapter.get_torch_dataloader()
    else:
        it = adapter.get_numpy_iterator()
    it = iter(it)
    next(it)
    next(it)
    with self.assertRaisesRegex(expected_exception_class, 'Expected exception'):
        next(it)