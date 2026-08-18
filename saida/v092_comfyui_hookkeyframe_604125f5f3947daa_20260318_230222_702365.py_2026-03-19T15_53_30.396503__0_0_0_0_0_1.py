def __init__(self, strength: float, start_percent=0.0, guarantee_steps=1):
    self.strength = strength
    self.start_percent = float(start_percent)
    self.start_t = 999999999.9
    self.guarantee_steps = guarantee_steps