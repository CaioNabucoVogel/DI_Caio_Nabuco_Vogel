def set_parameters(self, shift=1.0, timesteps=1000, multiplier=1000):
    self.shift = shift
    self.multiplier = multiplier
    ts = self.sigma(torch.arange(1, timesteps + 1, 1) / timesteps * multiplier)
    self.register_buffer('sigmas', ts)