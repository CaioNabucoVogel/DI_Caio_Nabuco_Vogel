def get_type(self, hook_type: EnumHookType):
    return self._hook_dict.get(hook_type, [])