def test_speedup(self):
    x = np.random.random((40, 4))
    y = np.random.random((40, 2))
    no_speedup_py_dataset = ExamplePyDataset(x, y, batch_size=4, delay=0.2)
    adapter = py_dataset_adapter.PyDatasetAdapter(no_speedup_py_dataset, shuffle=False)
    gen = adapter.get_numpy_iterator()
    t0 = time.time()
    for batch in gen:
        pass
    no_speedup_time = time.time() - t0
    speedup_py_dataset = ExamplePyDataset(x, y, batch_size=4, workers=4, max_queue_size=8, delay=0.2)
    adapter = py_dataset_adapter.PyDatasetAdapter(speedup_py_dataset, shuffle=False)
    gen = adapter.get_numpy_iterator()
    t0 = time.time()
    for batch in gen:
        pass
    speedup_time = time.time() - t0
    self.assertLess(speedup_time, no_speedup_time)