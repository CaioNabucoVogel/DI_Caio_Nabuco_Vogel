@staticmethod
@lru_cache
def _get_device_key(device: torch.device) -> Optional[str]:
    """
        Generate a device key for lookup table indexing.
        For CPU devices, returns None.
        For CUDA devices, returns the props.gcnArchName string.
        """
    if device.type != 'cuda':
        return None
    props = torch.cuda.get_device_properties(device.index)
    return props.gcnArchName