def set_keyframes_on_hooks(self, hook_kf: HookKeyframeGroup):
    if hook_kf is None:
        hook_kf = HookKeyframeGroup()
    else:
        hook_kf = hook_kf.clone()
    for hook in self.hooks:
        hook.hook_keyframe = hook_kf