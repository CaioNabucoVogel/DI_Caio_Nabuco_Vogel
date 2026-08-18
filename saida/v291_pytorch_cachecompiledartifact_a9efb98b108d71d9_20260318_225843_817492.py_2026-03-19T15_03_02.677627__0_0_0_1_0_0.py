@staticmethod
def _load_impl(cache_dir_ctx: AbstractContextManager[Any], key: str) -> CompiledArtifact:
    with cache_dir_ctx, config.patch(unsafe_skip_cache_dynamic_shape_guards=True):
        with torch._functorch.config.patch(strict_autograd_cache=True):
            from torch._functorch._aot_autograd.autograd_cache import AOTAutogradCache
            result = AOTAutogradCache._lookup(key, local=True, remote=False, args=[], cache_info={}, aot_config=None)
        assert result is not None
        (entry, _) = result
        from .compile_fx import _CompileFxKwargs
        fx_config = _CompileFxKwargs(cudagraphs=BoxedBool(False), boxed_forward_device_index=BoxedDeviceIndex(0))
        context = torch._guards.TracingContext(FakeTensorMode(shape_env=ShapeEnv()))
        with torch._guards.tracing(context):
            compiled_fn = entry.wrap_post_compile([], entry.sanitized_aot_config, fx_config)
    return CacheCompiledArtifact(lambda *args: compiled_fn(list(args)), None)