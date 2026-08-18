class _MakefxTracer:

    def __init__(self, decomposition_table: Optional[Mapping[OpOverload, Callable]], tracing_mode: str, _allow_non_fake_inputs: bool, pre_dispatch: bool, record_module_stack: bool, _allow_fake_constant: bool, _error_on_data_dependent_ops: bool, record_stack_traces: bool=False, parent_tracer: Optional[_MakefxTracer]=None, proxy_module_inputs: bool=False, _disable_torch_fn_metadata_mode: bool=False) -> None:
        self.decomposition_table: dict[OpOverload, Callable] = dict(decomposition_table or {})
        self.decomposition_table.setdefault(torch.ops.aten.sym_numel.default, torch._decomp.decompositions.sym_numel)
        self.tracing_mode: str = tracing_mode
        self._allow_non_fake_inputs: bool = _allow_non_fake_inputs
        self.pre_dispatch: bool = pre_dispatch
        self.record_module_stack: bool = record_module_stack
        self._allow_fake_constant: bool = _allow_fake_constant
        self._error_on_data_dependent_ops: bool = _error_on_data_dependent_ops
        self.fake_tensor_mode: Optional[FakeTensorMode] = None
        self.proxy_mode: Union[nullcontext, ProxyTorchDispatchMode] = nullcontext()
        self.proxy_function_mode: Union[nullcontext, PreDispatchTorchFunctionMode] = nullcontext()
        self.fx_tracer: Optional[PythonKeyTracer] = None
        self.python_dispatcher_mode: Union[nullcontext, Any] = nullcontext()
        self.torch_fn_metadata_mode: Union[nullcontext, TorchFunctionMetadataMode] = nullcontext()
        self.record_stack_traces = record_stack_traces
        self.parent_tracer: Optional[_MakefxTracer] = parent_tracer
        self.proxy_module_inputs = proxy_module_inputs
        self._disable_torch_fn_metadata_mode = _disable_torch_fn_metadata_mode

    def _checkpoint_modes(self) -> list[Any]:
        return [self.fake_tensor_mode, self.proxy_mode, self.proxy_function_mode, self.fx_tracer, self.python_dispatcher_mode, self.torch_fn_metadata_mode]

    def _restore_modes(self, prev_fake_tensor_mode: Optional[FakeTensorMode], prev_proxy_mode: Union[nullcontext, ProxyTorchDispatchMode], prev_proxy_function_mode: Union[nullcontext, PreDispatchTorchFunctionMode], prev_fx_tracer: Optional[PythonKeyTracer], prev_python_dispatcher_mode: Union[nullcontext, Any], prev_torch_fn_metadata_mode: Union[nullcontext, TorchFunctionMetadataMode]) -> None:
        self.fake_tensor_mode = prev_fake_tensor_mode
        self.proxy_mode = prev_proxy_mode
        self.proxy_function_mode = prev_proxy_function_mode
        self.fx_tracer = prev_fx_tracer
        self.python_dispatcher_mode = prev_python_dispatcher_mode
        self.torch_fn_metadata_mode = prev_torch_fn_metadata_mode

    @contextmanager
    def _init_modes_from_inputs(self, f: Callable, args: tuple[object, ...]) -> Generator[None, None, None]:
        prev_modes = self._checkpoint_modes()
        try:
            from .symbolic_shapes import ShapeEnv
            if hasattr(f, '_orig_mod') and self.record_module_stack:
                scope_root = f._orig_mod
                self.fx_tracer = _ModuleStackTracer(scope_root)
            else:
                self.fx_tracer = PythonKeyTracer()
                self.fx_tracer.record_stack_traces = self.record_stack_traces
                if self.record_stack_traces:
                    self.fx_tracer._record_forward_stack_traces_only = True
            if self.tracing_mode == 'fake':
                import torch._dynamo
                fake_tensor_mode = torch._dynamo.utils.detect_fake_mode(args)
                if fake_tensor_mode is None:
                    import torch._functorch.config as _config
                    with _config.patch(fake_tensor_allow_unsafe_data_ptr_access=False):
                        fake_tensor_mode = FakeTensorMode(allow_fallback_kernels=True, allow_non_fake_inputs=self._allow_non_fake_inputs, shape_env=ShapeEnv(), static_shapes=True)
                self.fake_tensor_mode = fake_tensor_mode
            elif self.tracing_mode == 'symbolic':
                import torch._dynamo
                fake_tensor_mode = torch._dynamo.utils.detect_fake_mode(args)
                if fake_tensor_mode is None:
                    shape_env = ShapeEnv()
                    import torch._functorch.config as _config
                    with _config.patch(fake_tensor_allow_unsafe_data_ptr_access=False):
                        fake_tensor_mode = FakeTensorMode(allow_fallback_kernels=False, allow_non_fake_inputs=self._allow_non_fake_inputs, shape_env=shape_env)
                assert fake_tensor_mode.shape_env is not None, "shape_env should be set if tracing with 'symbolic'"
                self.fake_tensor_mode = fake_tensor_mode
            elif not self.tracing_mode == 'real':
                raise AssertionError(f'Unexpected tracing type: {self.tracing_mode}')
            self._construct_modes_with_fx_tracer(self.fx_tracer)
            yield
        finally:
            self._restore_modes(*prev_modes)

    def _construct_modes_with_fx_tracer(self, fx_tracer: _ProxyTracer) -> None:
        self.proxy_mode = ProxyTorchDispatchMode(fx_tracer, self.tracing_mode, pre_dispatch=self.pre_dispatch, _allow_fake_constant=self._allow_fake_constant, _error_on_data_dependent_ops=self._error_on_data_dependent_ops)
        if self.pre_dispatch:
            self.proxy_function_mode = PreDispatchTorchFunctionMode(fx_tracer)
        if self.tracing_mode == 'symbolic' or self.pre_dispatch:
            self.python_dispatcher_mode = enable_python_dispatcher()
        if not self._disable_torch_fn_metadata_mode:
            self.torch_fn_metadata_mode = TorchFunctionMetadataMode(fx_tracer)
        fx_tracer.proxy_module_inputs = self.proxy_module_inputs

    @contextmanager
    def _init_modes_from_parent(self, parent_tracer: _MakefxTracer) -> Generator[None, None, None]:
        prev_modes = self._checkpoint_modes()
        try:
            self.fake_tensor_mode = parent_tracer.fake_tensor_mode

            def _create_sub_fx_tracer(parent_tracer: _ProxyTracer) -> PythonKeyTracer:
                if type(parent_tracer) is PythonKeyTracer:
                    return PythonKeyTracer()
                elif type(parent_tracer) is _ModuleStackTracer:
                    return _ModuleStackTracer(parent_tracer.scope_root)
                else:
                    raise RuntimeError(f'Unexpected tracer type: {type(parent_tracer)}.')
            assert parent_tracer.fx_tracer is not None
            self.fx_tracer = _create_sub_fx_tracer(parent_tracer.fx_tracer)
            self._construct_modes_with_fx_tracer(self.fx_tracer)
            yield
        finally:
            self._restore_modes(*prev_modes)

    def _trace_inner(self, f: Callable, *args: object) -> GraphModule:
        import torch._dynamo
        phs = pytree.tree_map(lambda _: torch.fx._symbolic_trace.PH, args)

        def _wrap_fake(args: T) -> T:
            arg_count = 0

            def inner_wrap_fake(x: object) -> object:
                nonlocal arg_count
                from torch._dynamo.source import ConstantSource
                assert self.fake_tensor_mode is not None
                source = ConstantSource(f'input{arg_count}')
                if isinstance(x, Tensor):
                    arg_count += 1
                    return self.fake_tensor_mode.from_tensor(x, source=source)
                elif type(x) is int and self.tracing_mode == 'symbolic':
                    assert self.fake_tensor_mode.shape_env is not None, "shape_env should be set if tracing with 'symbolic'"
                    return self.fake_tensor_mode.shape_env.create_symintnode(self.fake_tensor_mode.shape_env.create_symbol(x, source, positive=None), hint=x, source=source)
                elif isinstance(x, torch.ScriptObject) or is_opaque_value(x):
                    return torch._library.fake_class_registry.maybe_to_fake_obj(self.fake_tensor_mode, x)
                assert not isinstance(x, FakeScriptObject), f'ScriptObject {x} has been fakified. Cannot wrap_fake it again.'
                return x
            wrap_fn_map = {'real': lambda x: x, 'fake': inner_wrap_fake, 'symbolic': inner_wrap_fake}
            return pytree.tree_map(wrap_fn_map[self.tracing_mode], args)

        def _wrap_func(f: Callable[_P, R], phs: Sequence[PHBase]) -> Callable[_P, R]:
            if not hasattr(inspect.unwrap(f), '__code__') or inspect.unwrap(f).__code__.co_flags & inspect.CO_VARARGS:
                return fake_signature(f, len(phs))
            return f
        args = _wrap_fake(args)
        func = _wrap_func(f, phs)
        proxy_mode: ProxyTorchDispatchMode = typing.cast(ProxyTorchDispatchMode, self.proxy_mode)
        with ExitStack() as stack:
            stack.enter_context(decompose(self.decomposition_table))
            if self.fake_tensor_mode:
                stack.enter_context(self.fake_tensor_mode)
            stack.enter_context(self.python_dispatcher_mode)
            stack.enter_context(self.proxy_function_mode)
            stack.enter_context(self.torch_fn_metadata_mode)
            stack.enter_context(proxy_mode)
            stack.enter_context(disable_autocast_cache())
            stack.enter_context(_set_make_fx_tracer(self))
            assert self.fx_tracer is not None
            try:
                t = dispatch_trace(wrap_key(func, args, self.fx_tracer, self.pre_dispatch), tracer=self.fx_tracer, concrete_args=tuple(phs))
            except Exception:
                trace_structured('artifact', metadata_fn=lambda : {'name': 'make_fx_fail_partial', 'encoding': 'string'}, payload_fn=lambda : self.fx_tracer.graph.python_code(root_module='self', verbose=True, include_stride=True, include_device=True).src)
                raise
        if self.is_hop_subgraph_tracer() and (fake_mode := torch._guards.detect_fake_mode(args)) and (fake_mode.shape_env is not None):
            from torch.fx.passes.runtime_assert import insert_deferred_runtime_asserts
            insert_deferred_runtime_asserts(t, fake_mode.shape_env, 'reenter_make_fx')
            t.recompile()
        if self.tracing_mode == 'symbolic':
            assert self.fake_tensor_mode is not None
            t.shape_env = self.fake_tensor_mode.shape_env
        return t

    def trace(self, f: Callable, *args: object) -> fx.GraphModule:
        with self._init_modes_from_inputs(f, args):
            return self._trace_inner(f, *args)

    def is_hop_subgraph_tracer(self) -> bool:
        return self.parent_tracer is not None

    def trace_subgraph(self, f: Callable, *args: object) -> GraphModule:
        sub_tracer = _MakefxTracer(self.decomposition_table, 'real', self._allow_non_fake_inputs, self.pre_dispatch, self.record_module_stack, self._allow_fake_constant, self._error_on_data_dependent_ops, parent_tracer=self)
        with sub_tracer._init_modes_from_parent(self):
            return sub_tracer._trace_inner(f, *args)

    def trace_subgraph_custom_decomp(self, f: Callable, decomp_table: Mapping[OpOverload, Callable], *args) -> GraphModule:
        assert isinstance(decomp_table, Mapping)
        sub_tracer = _MakefxTracer(decomp_table, 'real', self._allow_non_fake_inputs, self.pre_dispatch, self.record_module_stack, self._allow_fake_constant, self._error_on_data_dependent_ops, parent_tracer=self)
        with sub_tracer._init_modes_from_parent(self):
            return sub_tracer._trace_inner(f, *args)