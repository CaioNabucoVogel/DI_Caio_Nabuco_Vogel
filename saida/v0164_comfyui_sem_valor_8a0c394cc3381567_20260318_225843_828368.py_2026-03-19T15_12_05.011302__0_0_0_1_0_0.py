def force_load_param(self, param_key, device_to):
    key = key_param_name_to_key(n, param_key)
    if key in self.backup:
        comfy.utils.set_attr_param(self.model, key, self.backup[key].weight)
    self.patch_weight_to_device(key, device_to=device_to)
    (weight, _, _) = get_key_weight(self.model, key)
    if weight is not None:
        self.model.model_loaded_weight_memory += weight.numel() * weight.element_size()