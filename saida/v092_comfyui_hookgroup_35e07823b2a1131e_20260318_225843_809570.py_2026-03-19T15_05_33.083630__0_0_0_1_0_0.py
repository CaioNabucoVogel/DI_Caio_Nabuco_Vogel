def new_with_common_hooks(self, other: HookGroup):
    c = HookGroup()
    for hook in self.hooks:
        if other.contains(hook):
            c.add(hook.clone())
    return c