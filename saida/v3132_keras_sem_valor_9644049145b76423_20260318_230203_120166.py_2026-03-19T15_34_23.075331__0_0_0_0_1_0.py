@property
def kernel(self):
    if not self.built:
        raise AttributeError('You must build the layer before accessing `kernel`.')
    if self.lora_enabled:
        return self._kernel + self.lora_alpha / self.lora_rank * ops.matmul(self.lora_kernel_a, self.lora_kernel_b)
    return self._kernel