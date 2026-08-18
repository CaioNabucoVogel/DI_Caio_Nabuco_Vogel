def set_sigmas(self, sigmas):
    self.register_buffer('sigmas', sigmas.float())
    self.register_buffer('log_sigmas', sigmas.log().float())