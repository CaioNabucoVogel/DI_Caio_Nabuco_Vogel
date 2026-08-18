def convolution_op(self, inputs, kernel):
    return ops.conv(inputs, kernel, strides=list(self.strides), padding=self.padding, dilation_rate=self.dilation_rate, data_format=self.data_format)