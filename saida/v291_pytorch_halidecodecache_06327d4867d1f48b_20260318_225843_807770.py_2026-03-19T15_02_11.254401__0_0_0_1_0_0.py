@classmethod
def generate_halide(cls, *args: Any, **kwargs: Any) -> Callable[[], Any]:
    return cls.generate_halide_async(*args, **kwargs)()