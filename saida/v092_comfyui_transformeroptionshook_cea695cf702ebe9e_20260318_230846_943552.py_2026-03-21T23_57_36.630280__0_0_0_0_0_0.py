class TransformerOptionsHook(Hook):
    """
    Hook responsible for adding wrappers, callbacks, patches, or anything else related to transformer_options.
    """

    def __init__(self, transformers_dict: dict[str, dict[str, dict[str, list[Callable]]]]=None, hook_scope=EnumHookScope.AllConditioning):
        super().__init__(hook_type=EnumHookType.TransformerOptions)
        self.transformers_dict = transformers_dict
        self.hook_scope = hook_scope
        self._skip_adding = False
        'Internal value used to avoid double load of transformer_options when hook_scope is AllConditioning.'

    def clone(self):
        c: TransformerOptionsHook = super().clone()
        c.transformers_dict = self.transformers_dict
        c._skip_adding = self._skip_adding
        return c

    def add_hook_patches(self, model: ModelPatcher, model_options: dict, target_dict: dict[str], registered: HookGroup):
        if not self.should_register(model, model_options, target_dict, registered):
            return False
        self._skip_adding = False
        if self.hook_scope == EnumHookScope.AllConditioning:
            add_model_options = {'transformer_options': self.transformers_dict, 'to_load_options': self.transformers_dict}
            self._skip_adding = True
        else:
            add_model_options = {'to_load_options': self.transformers_dict}
        registered.add(self)
        comfy.patcher_extension.merge_nested_dicts(model_options, add_model_options, copy_dict1=False)
        return True

    def on_apply_hooks(self, model: ModelPatcher, transformer_options: dict[str]):
        if not self._skip_adding:
            comfy.patcher_extension.merge_nested_dicts(transformer_options, self.transformers_dict, copy_dict1=False)