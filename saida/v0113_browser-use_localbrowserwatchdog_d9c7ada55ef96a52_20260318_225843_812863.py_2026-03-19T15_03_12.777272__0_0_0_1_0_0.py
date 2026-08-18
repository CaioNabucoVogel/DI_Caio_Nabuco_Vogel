@property
def browser_pid(self) -> int | None:
    """Get the browser process ID."""
    if self._subprocess:
        return self._subprocess.pid
    return None