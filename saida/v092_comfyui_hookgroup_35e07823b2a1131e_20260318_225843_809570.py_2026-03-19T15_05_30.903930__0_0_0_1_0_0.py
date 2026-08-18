def is_subset_of(self, other: HookGroup):
    self_hooks = set(self.hooks)
    other_hooks = set(other.hooks)
    return self_hooks.issubset(other_hooks)