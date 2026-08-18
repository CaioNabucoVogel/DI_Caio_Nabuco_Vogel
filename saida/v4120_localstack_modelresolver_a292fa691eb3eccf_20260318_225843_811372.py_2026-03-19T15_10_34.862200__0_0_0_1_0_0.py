@contextlib.contextmanager
def _resolving_ctx(self, current_resolving_name: str):
    self._current_resolving_name = current_resolving_name
    yield
    self._current_resolving_name = None