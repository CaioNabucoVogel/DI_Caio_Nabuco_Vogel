def add(self, hook: Hook):
    if hook not in self.hooks:
        self.hooks.append(hook)
        self._hook_dict.setdefault(hook.hook_type, []).append(hook)