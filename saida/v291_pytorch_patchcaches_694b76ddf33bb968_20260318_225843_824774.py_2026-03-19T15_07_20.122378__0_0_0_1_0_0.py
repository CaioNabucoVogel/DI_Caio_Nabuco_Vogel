@classmethod
def tearDown(cls):
    for name in _CACHE_CONFIG_EN:
        delattr(config, name)
        if name in cls._savedCacheState:
            setattr(config, name, cls._savedCacheState[name])