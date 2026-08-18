def __init__(self, config, device=None, dtype=None, ops=None):
    super().__init__()
    self.layers = nn.ModuleList([Block(config, device=device, dtype=dtype, ops=ops) for _ in range(config.num_hidden_layers)])