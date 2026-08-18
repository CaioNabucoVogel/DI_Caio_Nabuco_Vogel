def make_kernel_render(out_node, hint_override: Optional[int]=None):
    assert result is not None
    kernel = self.kernel_type(kernel_name=str(Placeholder.KERNEL_NAME), output_node=out_node, workspace_arg=workspace_arg, use_jit=False, hint_override=hint_override, tma_store=tma_store, transpose_discontiguous_tensor_descriptors_override=transpose_discontiguous_tensor_descriptors_override, **options)
    render = functools.partial(kernel.render, self.template, kwargs)
    return (kernel, render)