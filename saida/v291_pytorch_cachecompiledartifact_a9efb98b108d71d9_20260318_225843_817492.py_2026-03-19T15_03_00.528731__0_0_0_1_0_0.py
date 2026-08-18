def __call__(self, *args: Any) -> Any:
    return self._compiled_fn(*args)