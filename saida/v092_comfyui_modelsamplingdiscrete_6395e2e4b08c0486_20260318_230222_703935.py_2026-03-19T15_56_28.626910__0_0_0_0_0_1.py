def percent_to_sigma(self, percent):
    if percent <= 0.0:
        return 999999999.9
    if percent >= 1.0:
        return 0.0
    percent = 1.0 - percent
    return self.sigma(torch.tensor(percent * 999.0)).item()