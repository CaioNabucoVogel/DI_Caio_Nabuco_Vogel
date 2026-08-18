def _process_indexing(self, index):
    """Process and rename indexing, adding symbols as kernel inputs."""
    return self.kernel.kexpr(self.kernel.rename_indexing(index))