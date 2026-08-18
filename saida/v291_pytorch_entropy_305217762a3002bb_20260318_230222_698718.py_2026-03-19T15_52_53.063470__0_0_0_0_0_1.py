def entropy(self):
    return math.log(4 * math.pi) + self.scale.log()