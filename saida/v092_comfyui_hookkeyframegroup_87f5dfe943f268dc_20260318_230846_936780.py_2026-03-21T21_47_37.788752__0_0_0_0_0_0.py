class HookKeyframeGroup:

    def __init__(self):
        self.keyframes: list[HookKeyframe] = []
        self._current_keyframe: HookKeyframe = None
        self._current_used_steps = 0
        self._current_index = 0
        self._current_strength = None
        self._curr_t = -1.0

    @property
    def strength(self):
        if self._current_keyframe is not None:
            return self._current_keyframe.strength
        return 1.0

    def reset(self):
        self._current_keyframe = None
        self._current_used_steps = 0
        self._current_index = 0
        self._current_strength = None
        self.curr_t = -1.0
        self._set_first_as_current()

    def add(self, keyframe: HookKeyframe):
        self.keyframes.append(keyframe)
        self.keyframes = get_sorted_list_via_attr(self.keyframes, 'start_percent')
        self._set_first_as_current()

    def _set_first_as_current(self):
        if len(self.keyframes) > 0:
            self._current_keyframe = self.keyframes[0]
        else:
            self._current_keyframe = None

    def has_guarantee_steps(self):
        for kf in self.keyframes:
            if kf.guarantee_steps > 0:
                return True
        return False

    def has_index(self, index: int):
        return index >= 0 and index < len(self.keyframes)

    def is_empty(self):
        return len(self.keyframes) == 0

    def clone(self):
        c = HookKeyframeGroup()
        for keyframe in self.keyframes:
            c.keyframes.append(keyframe.clone())
        c._set_first_as_current()
        return c

    def initialize_timesteps(self, model: BaseModel):
        for keyframe in self.keyframes:
            keyframe.start_t = model.model_sampling.percent_to_sigma(keyframe.start_percent)

    def prepare_current_keyframe(self, curr_t: float, transformer_options: dict[str, torch.Tensor]) -> bool:
        if self.is_empty():
            return False
        if curr_t == self._curr_t:
            return False
        max_sigma = torch.max(transformer_options['sample_sigmas'])
        prev_index = self._current_index
        prev_strength = self._current_strength
        if self._current_used_steps >= self._current_keyframe.get_effective_guarantee_steps(max_sigma):
            if self.has_index(self._current_index + 1):
                for i in range(self._current_index + 1, len(self.keyframes)):
                    eval_c = self.keyframes[i]
                    if eval_c.start_t >= curr_t:
                        self._current_index = i
                        self._current_strength = eval_c.strength
                        self._current_keyframe = eval_c
                        self._current_used_steps = 0
                        if self._current_keyframe.get_effective_guarantee_steps(max_sigma) > 0:
                            break
                    else:
                        break
        self._current_used_steps += 1
        self._curr_t = curr_t
        return prev_index != self._current_index and prev_strength != self._current_strength