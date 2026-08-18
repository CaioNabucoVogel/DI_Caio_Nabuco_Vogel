def test_max_pooling3d(self, pool_size, strides, padding, data_format):
    inputs = np.arange(240, dtype='float32').reshape((2, 3, 4, 5, 2))
    layer = layers.MaxPooling3D(pool_size=pool_size, strides=strides, padding=padding, data_format=data_format)
    outputs = layer(inputs)
    expected = np_maxpool3d(inputs, pool_size, strides, padding, data_format)
    self.assertAllClose(outputs, expected)