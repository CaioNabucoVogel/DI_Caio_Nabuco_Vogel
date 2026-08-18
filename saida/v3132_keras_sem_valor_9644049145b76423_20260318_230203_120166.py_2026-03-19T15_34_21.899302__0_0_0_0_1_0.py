def build(self, input_shape):
    if self.data_format == 'channels_last':
        channel_axis = -1
        input_channel = input_shape[-1]
    else:
        channel_axis = 1
        input_channel = input_shape[1]
    self.input_spec = InputSpec(min_ndim=self.rank + 2, axes={channel_axis: input_channel})
    if input_channel % self.groups != 0:
        raise ValueError(f'The number of input channels must be evenly divisible by the number of groups. Received groups={self.groups}, but the input has {input_channel} channels (full input shape is {input_shape}).')
    kernel_shape = self.kernel_size + (input_channel // self.groups, self.filters)
    self.compute_output_shape(input_shape)
    self._kernel = self.add_weight(name='kernel', shape=kernel_shape, initializer=self.kernel_initializer, regularizer=self.kernel_regularizer, constraint=self.kernel_constraint, trainable=True, dtype=self.dtype)
    if self.use_bias:
        self.bias = self.add_weight(name='bias', shape=(self.filters,), initializer=self.bias_initializer, regularizer=self.bias_regularizer, constraint=self.bias_constraint, trainable=True, dtype=self.dtype)
    else:
        self.bias = None
    self.built = True
    if self.lora_rank:
        self.enable_lora(self.lora_rank, lora_alpha=self.lora_alpha)