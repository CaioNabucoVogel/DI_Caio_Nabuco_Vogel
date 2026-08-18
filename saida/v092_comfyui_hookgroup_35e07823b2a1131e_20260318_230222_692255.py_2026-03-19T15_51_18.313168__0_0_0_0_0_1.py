def clone_and_combine(self, other: HookGroup):
    c = self.clone()
    if other is not None:
        for hook in other.hooks:
            c.add(hook.clone())
    return c