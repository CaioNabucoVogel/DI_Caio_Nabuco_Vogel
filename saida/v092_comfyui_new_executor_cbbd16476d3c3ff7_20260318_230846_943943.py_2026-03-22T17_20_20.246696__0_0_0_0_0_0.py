def new_executor(cls, original: Callable, wrappers: list[Callable], idx=0):
    return cls(original, class_obj=None, wrappers=wrappers, idx=idx)