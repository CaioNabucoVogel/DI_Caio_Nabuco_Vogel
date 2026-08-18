def __init__(self, in_channels, out_channels, factor_t, factor_s=1):
    super().__init__()
    self.in_channels = in_channels
    self.out_channels = out_channels
    self.factor_t = factor_t
    self.factor_s = factor_s
    self.factor = self.factor_t * self.factor_s * self.factor_s
    assert in_channels * self.factor % out_channels == 0
    self.group_size = in_channels * self.factor // out_channels