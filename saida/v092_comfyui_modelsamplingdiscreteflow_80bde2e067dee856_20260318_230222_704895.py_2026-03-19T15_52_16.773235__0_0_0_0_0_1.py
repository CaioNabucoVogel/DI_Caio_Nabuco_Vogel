def percent_to_sigma(self, percent):
    if percent <= 0.0:
        return 1.0
    if percent >= 1.0:
        return 0.0
    return time_snr_shift(self.shift, 1.0 - percent)