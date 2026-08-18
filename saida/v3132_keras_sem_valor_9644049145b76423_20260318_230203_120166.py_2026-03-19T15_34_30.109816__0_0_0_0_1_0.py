def load_own_variables(self, store):
    if not self.lora_enabled:
        self._check_load_own_variables(store)
    if not self.built:
        return
    target_variables = [self._kernel]
    if self.use_bias:
        target_variables.append(self.bias)
    for (i, variable) in enumerate(target_variables):
        variable.assign(store[str(i)])
    if self.lora_enabled:
        self.lora_kernel_a.assign(ops.zeros(self.lora_kernel_a.shape))
        self.lora_kernel_b.assign(ops.zeros(self.lora_kernel_b.shape))