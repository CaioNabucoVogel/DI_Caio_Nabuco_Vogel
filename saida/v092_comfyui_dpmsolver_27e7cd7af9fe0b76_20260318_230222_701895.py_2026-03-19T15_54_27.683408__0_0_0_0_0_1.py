def dpm_solver_3_step(self, x, t, t_next, r1=1 / 3, r2=2 / 3, eps_cache=None):
    eps_cache = {} if eps_cache is None else eps_cache
    h = t_next - t
    (eps, eps_cache) = self.eps(eps_cache, 'eps', x, t)
    s1 = t + r1 * h
    s2 = t + r2 * h
    u1 = x - self.sigma(s1) * (r1 * h).expm1() * eps
    (eps_r1, eps_cache) = self.eps(eps_cache, 'eps_r1', u1, s1)
    u2 = x - self.sigma(s2) * (r2 * h).expm1() * eps - self.sigma(s2) * (r2 / r1) * ((r2 * h).expm1() / (r2 * h) - 1) * (eps_r1 - eps)
    (eps_r2, eps_cache) = self.eps(eps_cache, 'eps_r2', u2, s2)
    x_3 = x - self.sigma(t_next) * h.expm1() * eps - self.sigma(t_next) / r2 * (h.expm1() / h - 1) * (eps_r2 - eps)
    return (x_3, eps_cache)