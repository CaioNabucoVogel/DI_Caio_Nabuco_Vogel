def load(self, name: str, index: sympy.Expr):
    """Handle loading from tensor or fixed input."""
    if name not in self.fixed_inputs:
        index_str = self._process_indexing(index)
        var = self._add_kernel_input(name)
        buffer = V.graph.get_buffer(name)
        var_dtype = buffer.dtype
        line = f'tl.load({var} + {index_str})'
        if var_dtype in (torch.float16, torch.bfloat16) and config.triton.codegen_upcast_to_fp32:
            line += '.to(tl.float32)'
            var_dtype = torch.float32
        out = self.kernel.cse.generate(self.kernel.compute, line, dtype=var_dtype, shape=())
        return out
    return self.kernel.cse.generate(self.kernel.compute, f'({self.fixed_inputs[name]})', dtype=torch.float32, shape=())