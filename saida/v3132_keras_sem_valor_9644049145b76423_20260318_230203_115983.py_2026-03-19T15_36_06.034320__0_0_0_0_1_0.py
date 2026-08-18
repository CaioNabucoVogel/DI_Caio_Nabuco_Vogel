def _get_common_kwargs_for_sublayer(self):
    common_kwargs = dict(kernel_regularizer=self._kernel_regularizer, bias_regularizer=self._bias_regularizer, activity_regularizer=self._activity_regularizer, kernel_constraint=self._kernel_constraint, bias_constraint=self._bias_constraint, dtype=self.dtype_policy)
    kernel_initializer = self._kernel_initializer.__class__.from_config(self._kernel_initializer.get_config())
    bias_initializer = self._bias_initializer.__class__.from_config(self._bias_initializer.get_config())
    common_kwargs['kernel_initializer'] = kernel_initializer
    common_kwargs['bias_initializer'] = bias_initializer
    return common_kwargs