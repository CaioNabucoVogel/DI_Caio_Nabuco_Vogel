def clone(self):
    c = HookKeyframe(strength=self.strength, start_percent=self.start_percent, guarantee_steps=self.guarantee_steps)
    c.start_t = self.start_t
    return c