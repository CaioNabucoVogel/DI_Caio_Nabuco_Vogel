def eps(self, eps_cache, key, x, t, *args, **kwargs):
    if key in eps_cache:
        return (eps_cache[key], eps_cache)
    sigma = self.sigma(t) * x.new_ones([x.shape[0]])
    eps = (x - self.model(x, sigma, *args, **self.extra_args, **kwargs)) / self.sigma(t)
    if self.eps_callback is not None:
        self.eps_callback()
    return (eps, {key: eps, **eps_cache})