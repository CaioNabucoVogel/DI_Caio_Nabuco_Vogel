def sigma(self, timestep):
    return time_snr_shift(self.shift, timestep / self.multiplier)