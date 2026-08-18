def __exit__(self, exc_type: Optional[type[BaseException]], exc_value: Optional[BaseException], traceback: Optional[TracebackType]) -> None:
    self._stack.__exit__(exc_type, exc_value, traceback)