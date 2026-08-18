class CompiledArtifact(ABC):
    """
    CompiledArtifact class represents the inductor cache artifacts that
    can be invoked in order to avoid repeated compilation.

    CompiledArtifact can be obtained by calling standalone_compile(gm, example_inputs)
    to create a fresh CompiledArtifact from a GraphModule and example inputs.

    Later this CompiledArtifact can be saved to disk, either as a binary or unpacked
    into the provided folder via the CompiledArtifact.save function.

    CompiledArtifact.load provides a way to create a CompiledArtifact from the
    binary or unpacked data.

    Finally, the CompiledArtifact can be invoked via the __call__ method
    to execute the cached artifact.
    """

    def __init__(self, compiled_fn: Callable[..., Any], artifacts: Optional[tuple[bytes, CacheInfo]]):
        self._compiled_fn = compiled_fn
        self._artifacts = artifacts

    @abstractmethod
    def __call__(self, *args: Any) -> Any:
        ...

    @abstractmethod
    def save(self, *, path: str, format: Literal['binary', 'unpacked']='binary') -> None:
        ...

    @staticmethod
    def load(*, path: str, format: Literal['binary', 'unpacked']='binary') -> CompiledArtifact:
        if format == 'unpacked':
            return CacheCompiledArtifact.load(path=path, format=format)
        assert format == 'binary'
        with open(path, 'rb') as file:
            from torch.utils._appending_byte_serializer import BytesReader
            from .codecache import torch_key
            result_bytes = file.read()
            reader = BytesReader(result_bytes)
            header = reader.read_bytes()
            if header == AOTCompiledArtifact.AOT_HEADER:
                assert reader.read_bytes() == torch_key()
                artifact = reader.read_bytes()
                assert reader.is_finished()
                return AOTCompiledArtifact.deserialize(artifact)
            elif header == CacheCompiledArtifact.CACHE_HEADER:
                assert reader.read_bytes() == torch_key()
                key = reader.read_str()
                artifact_bytes = reader.read_bytes()
                assert reader.is_finished()
                torch.compiler.load_cache_artifacts(artifact_bytes)
                return CacheCompiledArtifact._load_impl(nullcontext(), key)
            else:
                raise RuntimeError('Invalid header, expected CacheCompiledArtifact or AOTCompiledArtifact, got: ' + header.decode('utf-8'))