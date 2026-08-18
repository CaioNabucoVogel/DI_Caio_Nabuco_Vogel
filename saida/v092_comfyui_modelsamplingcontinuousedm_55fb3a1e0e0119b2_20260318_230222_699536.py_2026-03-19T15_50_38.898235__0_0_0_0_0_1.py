def set_parameters(self, sigma_min, sigma_max, sigma_data):
    self.sigma_data = sigma_data
    sigmas = torch.linspace(math.log(sigma_min), math.log(sigma_max), 1000).exp()
    self.register_buffer('sigmas', sigmas)
    self.register_buffer('log_sigmas', sigmas.log())