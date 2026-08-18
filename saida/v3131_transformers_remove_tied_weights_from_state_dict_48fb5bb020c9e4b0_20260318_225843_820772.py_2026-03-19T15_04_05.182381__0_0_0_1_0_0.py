def remove_tied_weights_from_state_dict(state_dict: dict[str, torch.Tensor], model: 'PreTrainedModel') -> dict[str, torch.Tensor]:
    """
    Remove all tied weights from the given `state_dict`, making sure to keep only the main weight that `model`
    will expect when reloading (even if we know tie weights symmetrically, it's better to keep the intended one).
    This is because `safetensors` does not allow tensor aliasing - so we're going to remove aliases before saving.
    """
    ptrs = collections.defaultdict(list)
    for (name, tensor) in state_dict.items():
        if not isinstance(tensor, torch.Tensor):
            ptrs[id(tensor)].append(name)
        elif tensor.device.type == 'meta':
            tensor = model.get_parameter(name)
            ptrs[id(tensor)].append(name)
        else:
            ptrs[id_tensor_storage(tensor)].append(name)
    shared_ptrs = {ptr: names for (ptr, names) in ptrs.items() if len(names) > 1}
    all_potential_tied_weights_keys = set(_get_tied_weight_keys(model))
    error_names = []
    to_delete_names = set()
    if all_potential_tied_weights_keys is not None:
        for names in shared_ptrs.values():
            found = 0
            for name in sorted(names):
                matches_pattern = any((re.search(pat, name) for pat in all_potential_tied_weights_keys))
                if matches_pattern and name in state_dict:
                    found += 1
                    if found < len(names):
                        to_delete_names.add(name)
    (shared_names, disjoint_names) = _find_disjoint(shared_ptrs.values(), state_dict)
    for name in disjoint_names:
        state_dict[name] = state_dict[name].clone()
    (shared_names, identical_names) = _find_identical(shared_names, state_dict)
    for inames in identical_names:
        known = inames.intersection(to_delete_names)
        for name in known:
            del state_dict[name]
        unknown = inames.difference(to_delete_names)
        if len(unknown) > 1:
            error_names.append(unknown)
    if shared_names:
        error_names.extend(shared_names)
    if len(error_names) > 0:
        raise RuntimeError(f"The weights trying to be saved contained shared tensors {error_names} which are not properly defined. We found all the potential target tied weights keys to be: {all_potential_tied_weights_keys}.\nThis can also just mean that the module's tied weight keys are wrong vs the actual tied weights in the model.")
    return state_dict