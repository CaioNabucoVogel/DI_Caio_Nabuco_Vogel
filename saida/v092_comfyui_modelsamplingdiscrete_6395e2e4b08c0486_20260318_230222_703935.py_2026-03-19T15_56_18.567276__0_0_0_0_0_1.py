def timestep(self, sigma):
    log_sigma = sigma.log()
    dists = log_sigma.to(self.log_sigmas.device) - self.log_sigmas[:, None]
    return dists.abs().argmin(dim=0).view(sigma.shape).to(sigma.device)