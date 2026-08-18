def size(self):
    o = 0
    c = 1
    for c in self.cond:
        size = c.size()
        o += math.prod(size)
        if len(size) > 1:
            c = size[1]
    return [1, c, o // c]