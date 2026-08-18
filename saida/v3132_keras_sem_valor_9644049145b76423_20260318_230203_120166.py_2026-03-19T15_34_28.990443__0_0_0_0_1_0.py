def save_own_variables(self, store):
    if not self.built:
        return
    target_variables = [self.kernel]
    if self.use_bias:
        target_variables.append(self.bias)
    for (i, variable) in enumerate(target_variables):
        store[str(i)] = variable