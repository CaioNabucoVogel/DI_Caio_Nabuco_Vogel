def __getitem__(self, idx):
    if idx == 0:
        return (np.ones([16, 4], 'float32'), np.ones([16, 2], 'float32'))
    if idx == 1:
        return (np.ones([16, 5], 'float32'), np.ones([16, 2], 'float32'))
    else:
        return (np.ones([2, 6], 'float32'), np.ones([2, 2], 'float32'))