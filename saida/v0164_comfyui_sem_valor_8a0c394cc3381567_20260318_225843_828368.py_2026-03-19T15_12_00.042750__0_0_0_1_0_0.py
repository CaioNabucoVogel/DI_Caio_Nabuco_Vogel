def setup_param(self, m, n, param_key):
    nonlocal num_patches
    key = key_param_name_to_key(n, param_key)
    weight_function = []
    (weight, _, _) = get_key_weight(self.model, key)
    if weight is None:
        return (False, 0)
    if key in self.patches:
        if comfy.lora.calculate_shape(self.patches[key], weight, key) != weight.shape:
            return (True, 0)
        setattr(m, param_key + '_lowvram_function', LowVramPatch(key, self.patches))
        num_patches += 1
    else:
        setattr(m, param_key + '_lowvram_function', None)
    if key in self.weight_wrapper_patches:
        weight_function.extend(self.weight_wrapper_patches[key])
    setattr(m, param_key + '_function', weight_function)
    geometry = weight
    if not isinstance(weight, QuantizedTensor):
        model_dtype = getattr(m, param_key + '_comfy_model_dtype', None) or weight.dtype
        weight._model_dtype = model_dtype
        geometry = comfy.memory_management.TensorGeometry(shape=weight.shape, dtype=model_dtype)
    return (False, comfy.memory_management.vram_aligned_size(geometry))