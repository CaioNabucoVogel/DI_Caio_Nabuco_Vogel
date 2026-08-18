def _register_schedule(self, given_betas=None, beta_schedule='linear', timesteps=1000, linear_start=0.0001, linear_end=0.02, cosine_s=0.008, zsnr=False):
    if given_betas is not None:
        betas = given_betas
    else:
        betas = make_beta_schedule(beta_schedule, timesteps, linear_start=linear_start, linear_end=linear_end, cosine_s=cosine_s)
    alphas = 1.0 - betas
    alphas_cumprod = torch.cumprod(alphas, dim=0)
    (timesteps,) = betas.shape
    self.num_timesteps = int(timesteps)
    self.linear_start = linear_start
    self.linear_end = linear_end
    self.zsnr = zsnr
    sigmas = ((1 - alphas_cumprod) / alphas_cumprod) ** 0.5
    if self.zsnr:
        sigmas = rescale_zero_terminal_snr_sigmas(sigmas)
    self.set_sigmas(sigmas)