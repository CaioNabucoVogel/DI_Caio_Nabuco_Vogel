def test_stateful_batch_size_mismatch_raises(self):
    from keras.src.models import Functional
    batch_size = 4
    timesteps = 5
    features = 3
    layer = layers.RNN(TwoStatesRNNCell(2), stateful=True)
    inputs = layers.Input(shape=(timesteps, features), batch_size=batch_size)
    model = Functional(inputs, layer(inputs))
    x = ops.random.uniform(shape=(batch_size, timesteps, features))
    _ = model(x)
    with self.assertRaisesRegex(ValueError, 'batch size'):
        x_bad = ops.random.uniform(shape=(1, timesteps, features))
        model(x_bad)