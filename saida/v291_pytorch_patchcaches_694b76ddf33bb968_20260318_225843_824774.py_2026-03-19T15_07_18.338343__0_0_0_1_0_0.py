@classmethod
def setUp(cls):
    cls._savedCacheState = {}
    for name in _CACHE_CONFIG_EN:
        if hasattr(config, name):
            cls._savedCacheState[name] = getattr(config, name)
        setattr(config, name, False)