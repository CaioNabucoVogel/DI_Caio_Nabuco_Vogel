def remove(self, hook: Hook):
    if hook in self.hooks:
        self.hooks.remove(hook)
        self._hook_dict[hook.hook_type].remove(hook)