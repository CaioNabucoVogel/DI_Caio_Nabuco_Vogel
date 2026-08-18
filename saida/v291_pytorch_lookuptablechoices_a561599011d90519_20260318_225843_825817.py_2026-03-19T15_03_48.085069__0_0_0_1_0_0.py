def make_lookup_key_variants(self, kernel_inputs: KernelInputs, op_name: str) -> tuple[Optional[str], Optional[str]]:
    """
        Generate both device-specific and device-agnostic lookup keys.
        Override this method to customize key variant generation.

        Args:
            kernel_inputs: KernelInputs object containing input nodes and scalars
            op_name: Operation name (e.g., "mm", "addmm")

        Returns:
            Tuple of (device_key, device_agnostic_key). Either may be None if generation fails.
        """
    device_key = self.make_lookup_key(kernel_inputs, op_name, include_device=True)
    device_agnostic_key = self.make_lookup_key(kernel_inputs, op_name, include_device=False)
    return (device_key, device_agnostic_key)