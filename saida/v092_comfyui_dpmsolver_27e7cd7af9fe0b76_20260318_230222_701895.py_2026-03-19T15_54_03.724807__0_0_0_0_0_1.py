def __init__(self, model, extra_args=None, eps_callback=None, info_callback=None):
    super().__init__()
    self.model = model
    self.extra_args = {} if extra_args is None else extra_args
    self.eps_callback = eps_callback
    self.info_callback = info_callback