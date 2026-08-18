def test_passing_initial_state_two_states(self):
    sequence = np.ones((2, 3, 2))
    state = [np.ones((2, 2)), np.ones((2, 2))]
    layer = layers.RNN(TwoStatesRNNCell(2), return_sequences=False)
    output = layer(sequence, initial_state=state)
    self.assertAllClose(np.array([[44.0, 44.0], [44.0, 44.0]]), output)
    layer = layers.RNN(TwoStatesRNNCell(2), return_sequences=False, return_state=True)
    (output, state_1, state_2) = layer(sequence, initial_state=state)
    self.assertAllClose(np.array([[44.0, 44.0], [44.0, 44.0]]), output)
    self.assertAllClose(np.array([[22.0, 22.0], [22.0, 22.0]]), state_1)
    self.assertAllClose(np.array([[22.0, 22.0], [22.0, 22.0]]), state_2)