@classmethod
def load(cls, source_code: str, dst_file_ext: str) -> tuple[DLLWrapper, str, str]:
    """
        Compiles source code and loads the generated .so file.
        Returns a tuple of DLLWrapper, hash_key, source_code_path
        """
    if dst_file_ext != 'so':
        raise RuntimeError(f'Only support loading a .so file for now. Requested file extension: {dst_file_ext}. Source code: {source_code}')
    (dst_file_path, hash_key, source_code_path) = cls.compile(source_code, dst_file_ext)
    return (DLLWrapper(dst_file_path), hash_key, source_code_path)