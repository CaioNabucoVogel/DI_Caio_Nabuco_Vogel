@staticmethod
@lru_cache(maxsize=4)
def get_kernel_binary_remote_cache(caching_enabled: bool, caching_available: bool) -> Any | None:
    """
        Get or create the class instance of the CUTLASSKernelBinaryRemoteCache.

        Args:
            caching_enabled: Whether binary remote caching is enabled
            caching_available: Whether we're in fbcode environment

        Returns:
            CUTLASSKernelBinaryRemoteCache: The class instance of the kernel binary remote cache
        """
    if not caching_enabled:
        log.debug('CUTLASSKernelBinaryRemoteCache not requested, skipping')
        return None
    if not caching_available:
        return None
    try:
        from torch._inductor.fb.kernel_binary_remote_cache import CUTLASSKernelBinaryRemoteCache
        return CUTLASSKernelBinaryRemoteCache()
    except ImportError:
        log.debug('CUTLASSKernelBinaryRemoteCache not available, remote caching disabled')
        return None