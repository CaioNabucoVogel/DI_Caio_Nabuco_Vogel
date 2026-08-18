@classmethod
@lru_cache(None)
def write(cls, source_code: str, dst_file_ext: str) -> tuple[str, str]:
    """
        Writes source code into a file with dst_file_ext as the file extension.
        Returns the hash key of source code, and the path to the file.
        """
    if config.cuda.cutlass_hash_with_compile_cmd:
        cuda_command = repr(cuda_compile_command(['dummy_input'], 'dummy_output', dst_file_ext))
        extra = cuda_command
    else:
        extra = repr([_cuda_compiler(), _nvcc_compiler_options(), _nvcc_host_compiler_options(), cutlass_key()])
    (key, input_path) = write(source_code, cls._SOURCE_CODE_SUFFIX, extra=extra)
    return (key, input_path)