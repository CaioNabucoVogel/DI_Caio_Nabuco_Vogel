def __init__(self, model_config=None):
    super().__init__()
    if model_config is not None:
        sampling_settings = model_config.sampling_settings
    else:
        sampling_settings = {}
    self.set_parameters(shift=sampling_settings.get('shift', 1.0), multiplier=sampling_settings.get('multiplier', 1000))