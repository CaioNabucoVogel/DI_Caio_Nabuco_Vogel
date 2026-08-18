@staticmethod
def load(*, path: str, format: Literal['binary', 'unpacked']='binary') -> CompiledArtifact:
    (key, cache_dir_ctx) = CacheCompiledArtifact._prepare_load(path=path, format=format)
    return CacheCompiledArtifact._load_impl(cache_dir_ctx, key)