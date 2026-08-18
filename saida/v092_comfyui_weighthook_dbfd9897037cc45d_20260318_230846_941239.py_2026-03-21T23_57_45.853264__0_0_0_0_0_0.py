class WeightHook(Hook):
    """
    Hook responsible for tracking weights to be applied to some model/clip.

    Note, value of hook_scope is ignored and is treated as HookedOnly.
    """

    def __init__(self, strength_model=1.0, strength_clip=1.0):
        super().__init__(hook_type=EnumHookType.Weight, hook_scope=EnumHookScope.HookedOnly)
        self.weights: dict = None
        self.weights_clip: dict = None
        self.need_weight_init = True
        self._strength_model = strength_model
        self._strength_clip = strength_clip
        self.hook_scope = EnumHookScope.HookedOnly

    @property
    def strength_model(self):
        return self._strength_model * self.strength

    @property
    def strength_clip(self):
        return self._strength_clip * self.strength

    def add_hook_patches(self, model: ModelPatcher, model_options: dict, target_dict: dict[str], registered: HookGroup):
        if not self.should_register(model, model_options, target_dict, registered):
            return False
        weights = None
        target = target_dict.get('target', None)
        if target == EnumWeightTarget.Clip:
            strength = self._strength_clip
        else:
            strength = self._strength_model
        if self.need_weight_init:
            key_map = {}
            if target == EnumWeightTarget.Clip:
                key_map = comfy.lora.model_lora_keys_clip(model.model, key_map)
            else:
                key_map = comfy.lora.model_lora_keys_unet(model.model, key_map)
            weights = comfy.lora.load_lora(self.weights, key_map, log_missing=False)
        elif target == EnumWeightTarget.Clip:
            weights = self.weights_clip
        else:
            weights = self.weights
        model.add_hook_patches(hook=self, patches=weights, strength_patch=strength)
        registered.add(self)
        return True

    def clone(self):
        c: WeightHook = super().clone()
        c.weights = self.weights
        c.weights_clip = self.weights_clip
        c.need_weight_init = self.need_weight_init
        c._strength_model = self._strength_model
        c._strength_clip = self._strength_clip
        return c