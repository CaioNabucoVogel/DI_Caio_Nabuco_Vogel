def dpm_solver_1_step(self, x, t, t_next, eps_cache=None):
    eps_cache = {} if eps_cache is None else eps_cache
    h = t_next - t
    (eps, eps_cache) = self.eps(eps_cache, 'eps', x, t)
    x_1 = x - self.sigma(t_next) * h.expm1() * eps
    return (x_1, eps_cache)