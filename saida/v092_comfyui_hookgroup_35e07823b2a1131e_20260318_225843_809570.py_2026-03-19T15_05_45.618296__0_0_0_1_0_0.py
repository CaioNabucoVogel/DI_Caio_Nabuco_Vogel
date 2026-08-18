def reset(self):
    for hook in self.hooks:
        hook.reset()