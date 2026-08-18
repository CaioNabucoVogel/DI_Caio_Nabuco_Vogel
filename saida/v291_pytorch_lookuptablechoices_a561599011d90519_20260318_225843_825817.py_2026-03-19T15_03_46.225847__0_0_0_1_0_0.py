def make_lookup_key(self, kernel_inputs: KernelInputs, op_name: str, include_device: bool=False) -> Optional[str]:
    """
        Create a flattened lookup key from kernel inputs and operation name.
        Override this method to customize key generation.

        Args:
            kernel_inputs: KernelInputs object containing input nodes and scalars
            op_name: Operation name (e.g., "mm", "addmm")
            include_device: Whether to include device key in the generated key

        Returns:
            A string key combining device (optional), operation, and input information
        """
    device = kernel_inputs.device()
    dev_key = self._get_device_key(device)
    if dev_key is None:
        return None
    if not include_device:
        dev_key = None
    input_key = self._generate_kernel_inputs_key(kernel_inputs)
    if dev_key is not None:
        key_parts = [dev_key, input_key, op_name]
    else:
        key_parts = [input_key, op_name]
    return '+'.join(key_parts)