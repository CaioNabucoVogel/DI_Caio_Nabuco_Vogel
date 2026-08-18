def test_serialization(self):
    layer = layers.RNN(TwoStatesRNNCell(2), return_sequences=False)
    self.run_class_serialization_test(layer)
    layer = layers.RNN(OneStateRNNCell(2), return_sequences=False)
    self.run_class_serialization_test(layer)