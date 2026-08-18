def clone(self):
    c = HookGroup()
    for hook in self.hooks:
        c.add(hook.clone())
    return c