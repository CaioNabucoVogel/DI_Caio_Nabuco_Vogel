@classmethod
def _record_cuda_compile_error(cls, error_str: str, key_with_ext: str, cmd_parts: list[str], input_path: str, output_path: str, binary_remote_cache: Any=None) -> None:
    error_json = json.dumps([cmd_parts, error_str])
    cls.cache[key_with_ext] = CUDACodeCache.CacheEntry(input_path, output_path, error_json)
    error_path = binary_error_path(output_path)
    with open(error_path, 'w', encoding='utf-8') as fh:
        fh.write(error_json)
    if binary_remote_cache is not None and config.cuda.upload_to_binary_remote_cache:
        binary_remote_cache.put(error_path, config.cuda.binary_remote_cache_force_write)