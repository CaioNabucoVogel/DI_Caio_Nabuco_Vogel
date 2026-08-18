def __init__(self) -> None:
    self.autotune_local = _GlobalItemStats()
    self.autotune_remote = _GlobalItemStats()
    self.bundled_autotune = _GlobalItemStats()
    self.fx_graph = _GlobalItemStats()
    self.triton = _GlobalItemStats()
    self.aot_autograd = _GlobalItemStats()
    self.dynamo_pgo = _GlobalItemStats()