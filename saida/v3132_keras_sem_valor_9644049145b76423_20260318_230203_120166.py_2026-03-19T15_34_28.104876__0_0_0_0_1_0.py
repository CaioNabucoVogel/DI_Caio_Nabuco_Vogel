def enable_lora(self, rank, lora_alpha=None, a_initializer='he_uniform', b_initializer='zeros'):
    if self.kernel_constraint:
        raise ValueError('Lora is incompatible with kernel constraints. In order to enable lora on this layer, remove the `kernel_constraint` argument.')
    if not self.built:
        raise ValueError("Cannot enable lora on a layer that isn't yet built.")
    if self.lora_enabled:
        raise ValueError('lora is already enabled. This can only be done once per layer.')
    self._tracker.unlock()
    self.lora_kernel_a = self.add_weight(name='lora_kernel_a', shape=self._kernel.shape[:-1] + (rank,), initializer=initializers.get(a_initializer), regularizer=self.kernel_regularizer)
    self.lora_kernel_b = self.add_weight(name='lora_kernel_b', shape=(rank, self.filters), initializer=initializers.get(b_initializer), regularizer=self.kernel_regularizer)
    self._kernel.trainable = False
    self._tracker.lock()
    self.lora_enabled = True
    self.lora_rank = rank
    self.lora_alpha = lora_alpha if lora_alpha is not None else rank