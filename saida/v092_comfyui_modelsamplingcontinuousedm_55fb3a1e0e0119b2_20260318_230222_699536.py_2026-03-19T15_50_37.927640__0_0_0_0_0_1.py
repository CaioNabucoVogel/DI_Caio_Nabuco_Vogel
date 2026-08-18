def __init__(self, model_config=None):
    super().__init__()
    if model_config is not None:
        sampling_settings = model_config.sampling_settings
    else:
        sampling_settings = {}
    sigma_min = sampling_settings.get('sigma_min', 0.002)
    sigma_max = sampling_settings.get('sigma_max', 120.0)
    sigma_data = sampling_settings.get('sigma_data', 1.0)
    self.set_parameters(sigma_min, sigma_max, sigma_data)