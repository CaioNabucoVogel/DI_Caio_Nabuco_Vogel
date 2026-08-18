def get_config(self):
    config = super().get_config()
    config.update({'filters': self.filters, 'kernel_size': self.kernel_size, 'strides': self.strides, 'padding': self.padding, 'data_format': self.data_format, 'dilation_rate': self.dilation_rate, 'groups': self.groups, 'activation': activations.serialize(self.activation), 'use_bias': self.use_bias, 'kernel_initializer': initializers.serialize(self.kernel_initializer), 'bias_initializer': initializers.serialize(self.bias_initializer), 'kernel_regularizer': regularizers.serialize(self.kernel_regularizer), 'bias_regularizer': regularizers.serialize(self.bias_regularizer), 'activity_regularizer': regularizers.serialize(self.activity_regularizer), 'kernel_constraint': constraints.serialize(self.kernel_constraint), 'bias_constraint': constraints.serialize(self.bias_constraint)})
    if self.lora_rank:
        config['lora_rank'] = self.lora_rank
        config['lora_alpha'] = self.lora_alpha
    return config