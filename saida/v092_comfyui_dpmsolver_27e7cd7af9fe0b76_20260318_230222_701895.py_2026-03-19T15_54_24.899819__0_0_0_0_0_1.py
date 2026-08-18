def dpm_solver_2_step(self, x, t, t_next, r1=1 / 2, eps_cache=None):
    eps_cache = {} if eps_cache is None else eps_cache
    h = t_next - t
    (eps, eps_cache) = self.eps(eps_cache, 'eps', x, t)
    s1 = t + r1 * h
    u1 = x - self.sigma(s1) * (r1 * h).expm1() * eps
    (eps_r1, eps_cache) = self.eps(eps_cache, 'eps_r1', u1, s1)
    x_2 = x - self.sigma(t_next) * h.expm1() * eps - self.sigma(t_next) / (2 * r1) * h.expm1() * (eps_r1 - eps)
    return (x_2, eps_cache)