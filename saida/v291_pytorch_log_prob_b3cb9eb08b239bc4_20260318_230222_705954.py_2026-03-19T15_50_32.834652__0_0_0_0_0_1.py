def log_prob(self, value):
    if self._validate_args:
        self._validate_sample(value)
    return torch.xlogy(self.concentration - 1.0, value).sum(-1) + torch.lgamma(self.concentration.sum(-1)) - torch.lgamma(self.concentration).sum(-1)