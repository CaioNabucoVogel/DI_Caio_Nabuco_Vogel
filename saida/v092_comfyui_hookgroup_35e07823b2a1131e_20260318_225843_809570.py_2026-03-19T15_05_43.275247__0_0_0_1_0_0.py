def get_hooks_for_clip_schedule(self):
    scheduled_hooks: dict[WeightHook, list[tuple[tuple[float, float], HookKeyframe]]] = {}
    for hook in self.get_type(EnumHookType.Weight):
        hook: WeightHook
        hook_schedule = []
        if len(hook.hook_keyframe.keyframes) == 0:
            hook_schedule.append(((0.0, 1.0), None))
            scheduled_hooks[hook] = hook_schedule
            continue
        prev_keyframe = hook.hook_keyframe.keyframes[0]
        for keyframe in hook.hook_keyframe.keyframes:
            if keyframe.start_percent > prev_keyframe.start_percent and (not math.isclose(keyframe.strength, prev_keyframe.strength)):
                hook_schedule.append(((prev_keyframe.start_percent, keyframe.start_percent), prev_keyframe))
                prev_keyframe = keyframe
            elif keyframe.start_percent == prev_keyframe.start_percent:
                prev_keyframe = keyframe
        if not math.isclose(prev_keyframe.start_percent, 1.0):
            hook_schedule.append(((prev_keyframe.start_percent, 1.0), prev_keyframe))
        scheduled_hooks[hook] = hook_schedule
    all_ranges: list[tuple[float, float]] = []
    for range_kfs in scheduled_hooks.values():
        for (t_range, keyframe) in range_kfs:
            all_ranges.append(t_range)
    boundaries_set = set(itertools.chain.from_iterable(all_ranges))
    boundaries_set.add(0.0)
    boundaries = sorted(boundaries_set)
    real_ranges = [(boundaries[i], boundaries[i + 1]) for i in range(len(boundaries) - 1)]
    scheduled_keyframes: list[tuple[tuple[float, float], list[tuple[WeightHook, HookKeyframe]]]] = []
    for t_range in real_ranges:
        hooks_schedule = []
        for (hook, val) in scheduled_hooks.items():
            keyframe = None
            for (stored_range, stored_kf) in val:
                if stored_range[0] < t_range[1] and stored_range[1] > t_range[0]:
                    keyframe = stored_kf
                    break
            hooks_schedule.append((hook, keyframe))
        scheduled_keyframes.append((t_range, hooks_schedule))
    return scheduled_keyframes