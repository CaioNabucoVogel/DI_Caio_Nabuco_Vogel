def __init__(self, model_config=None, zsnr=None):
    super().__init__()
    if model_config is not None:
        sampling_settings = model_config.sampling_settings
    else:
        sampling_settings = {}
    beta_schedule = sampling_settings.get('beta_schedule', 'linear')
    linear_start = sampling_settings.get('linear_start', 0.00085)
    linear_end = sampling_settings.get('linear_end', 0.012)
    timesteps = sampling_settings.get('timesteps', 1000)
    if zsnr is None:
        zsnr = sampling_settings.get('zsnr', False)
    self._register_schedule(given_betas=None, beta_schedule=beta_schedule, timesteps=timesteps, linear_start=linear_start, linear_end=linear_end, cosine_s=0.008, zsnr=zsnr)
    self.sigma_data = 1.0