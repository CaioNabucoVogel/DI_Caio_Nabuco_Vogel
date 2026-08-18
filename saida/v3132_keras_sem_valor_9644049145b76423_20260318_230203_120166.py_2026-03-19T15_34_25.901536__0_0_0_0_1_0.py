def call(self, inputs):
    outputs = self.convolution_op(inputs, self.kernel)
    if self.use_bias:
        if self.data_format == 'channels_last':
            bias_shape = (1,) * (self.rank + 1) + (self.filters,)
        else:
            bias_shape = (1, self.filters) + (1,) * self.rank
        bias = ops.reshape(self.bias, bias_shape)
        outputs = ops.add(outputs, bias)
    if self.activation is not None:
        return self.activation(outputs)
    return outputs