def percent_to_sigma(self, percent):
    if percent <= 0.0:
        return 999999999.9
    if percent >= 1.0:
        return 0.0
    percent = 1.0 - percent
    log_sigma_min = math.log(self.sigma_min)
    return math.exp((math.log(self.sigma_max) - log_sigma_min) * percent + log_sigma_min)