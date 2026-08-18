def load() -> Callable[[], Any]:
    if wait_for_compile:
        wait_for_compile()
    return bindings_future()