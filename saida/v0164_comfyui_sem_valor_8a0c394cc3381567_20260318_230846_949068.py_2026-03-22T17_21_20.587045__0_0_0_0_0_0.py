def __init__(self, style_dim=512, motion_dim=20, dtype=None, device=None, operations=None):
    super().__init__()
    self.enc = Encoder(style_dim, motion_dim, dtype=dtype, device=device, operations=operations)
    self.dec = Synthesis(motion_dim, dtype=dtype, device=device, operations=operations)