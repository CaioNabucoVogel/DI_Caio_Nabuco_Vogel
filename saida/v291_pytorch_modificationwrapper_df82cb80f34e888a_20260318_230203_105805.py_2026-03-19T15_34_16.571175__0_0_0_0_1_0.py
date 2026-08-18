def _add_kernel_input(self, name: str):
    """Add name as input to kernel and return input ref."""
    return self.kernel.args.input(name)