class MockBackend(RemoteCacheBackend[Any]):

    def __init__(self, name: str) -> None:
        self._name = name

    @staticmethod
    def with_name(name: str) -> Callable[[], MockBackend]:

        def wrapper() -> MockBackend:
            return MockBackend(name)
        return wrapper

    @override
    def _get(self, key: str) -> Optional[Any]:
        stat = global_stats.get_stat(self._name)
        if key in stat.cache:
            stat += Stats(num_get_hit=1)
            return stat.cache.get(key)
        else:
            stat += Stats(num_get_miss=1)
            return None

    @override
    def _put(self, key: str, data: Any) -> None:
        stat = global_stats.get_stat(self._name)
        stat += Stats(num_put=1)
        stat.cache[key] = data