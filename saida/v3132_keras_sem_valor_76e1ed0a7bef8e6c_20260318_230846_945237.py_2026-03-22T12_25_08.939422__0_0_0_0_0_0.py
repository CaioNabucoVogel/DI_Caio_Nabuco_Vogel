def call(self, sequences, initial_state=None, mask=None, training=False):
    return super().call(sequences, mask=mask, training=training, initial_state=initial_state)