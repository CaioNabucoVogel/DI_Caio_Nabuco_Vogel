def __init__(self):
    self.hooks: list[Hook] = []
    self._hook_dict: dict[EnumHookType, list[Hook]] = {}