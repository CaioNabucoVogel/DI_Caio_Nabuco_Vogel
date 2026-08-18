def get_stat(self, name: str) -> _GlobalItemStats:
    return getattr(self, name)