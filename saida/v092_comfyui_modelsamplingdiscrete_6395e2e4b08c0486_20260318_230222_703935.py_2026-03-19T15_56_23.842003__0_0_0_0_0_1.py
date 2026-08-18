def sigma(self, timestep):
    t = torch.clamp(timestep.float().to(self.log_sigmas.device), min=0, max=len(self.sigmas) - 1)
    low_idx = t.floor().long()
    high_idx = t.ceil().long()
    w = t.frac()
    log_sigma = (1 - w) * self.log_sigmas[low_idx] + w * self.log_sigmas[high_idx]
    return log_sigma.exp().to(timestep.device)