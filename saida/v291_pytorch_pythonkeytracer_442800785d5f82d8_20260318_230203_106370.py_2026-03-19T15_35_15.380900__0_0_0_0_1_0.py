def call_module(self, m: Module, forward: Callable[..., Any], args: tuple[Any, ...], kwargs: dict[str, Any]) -> Any:
    return forward(*args, **kwargs)