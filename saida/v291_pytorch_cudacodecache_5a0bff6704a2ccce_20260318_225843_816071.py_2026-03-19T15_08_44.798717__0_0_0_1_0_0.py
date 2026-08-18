@staticmethod
def cache_clear() -> None:
    CUDACodeCache.cache.clear()
    CUDACodeCache.aot_kernels_o.clear()