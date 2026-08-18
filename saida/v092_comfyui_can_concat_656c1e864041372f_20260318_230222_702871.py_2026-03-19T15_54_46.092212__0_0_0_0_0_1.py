def can_concat(self, other):
    s1 = self.cond.shape
    s2 = other.cond.shape
    if s1 != s2:
        if s1[0] != s2[0] or s1[2] != s2[2]:
            return False
        mult_min = math.lcm(s1[1], s2[1])
        diff = mult_min // min(s1[1], s2[1])
        if diff > 4:
            return False
    if self.cond.device != other.cond.device:
        logging.warning('WARNING: conds not on same device: skipping concat.')
        return False
    return True