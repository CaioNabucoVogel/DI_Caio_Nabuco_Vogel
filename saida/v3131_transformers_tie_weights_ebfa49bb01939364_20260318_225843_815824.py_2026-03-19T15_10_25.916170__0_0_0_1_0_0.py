def tie_weights(self, missing_keys: set[str] | None=None, recompute_mapping: bool=True):
    """
        Tie the model weights. If `recompute_mapping=False` (default when called internally), it will rely on the
        `model.all_tied_weights_keys` attribute, containing the `{target: source}` mapping for the tied params.
        If `recompute_mapping=True`, it will re-check all internal submodels and their config to determine the params
        that need to be tied. This is the default when `model.tie_weights()` is called on its own, outside of
        `__init__`, and `from_pretrained`, in case the config values were changed somewhere.

        Note that during `from_pretrained`, tying is *symmetric*: if the mapping says "tie target -> source" but
        `source` is missing in the checkpoint while `target` exists, we *swap* source and target so we can still
        tie everything to the parameter that actually exists.
        """
    if not recompute_mapping:
        tied_keys = self.all_tied_weights_keys
    else:
        tied_keys = self.get_expanded_tied_weights_keys(all_submodels=True)
    tied_keys = list(tied_keys.items())
    for (i, (target_param_name, source_param_name)) in enumerate(tied_keys):
        if missing_keys is not None:
            remove_from_missing = True
            source_is_there = source_param_name not in missing_keys
            target_is_there = target_param_name not in missing_keys
            if source_is_there and target_is_there:
                logger.warning(f'The tied weights mapping and config for this model specifies to tie {source_param_name} to {target_param_name}, but both are present in the checkpoints, so we will NOT tie them. You should update the config with `tie_word_embeddings=False` to silence this warning')
                self.all_tied_weights_keys.pop(target_param_name)
                continue
            elif not source_is_there and target_is_there:
                (target_param_name, source_param_name) = (source_param_name, target_param_name)
            elif not source_is_there and (not target_is_there):
                for (target_backup, source_backup) in tied_keys[i + 1:]:
                    if source_backup == source_param_name:
                        target_backup_is_there = target_backup not in missing_keys
                        if target_backup_is_there:
                            source_param_name = target_backup
                            break
                else:
                    remove_from_missing = False
                    logger.warning(f'This checkpoint seem corrupted. The tied weights mapping for this model specifies to tie {source_param_name} to {target_param_name}, but both are absent from the checkpoint, and we could not find another related tied weight for those keys')
        source_param = self.get_parameter_or_buffer(source_param_name)
        if '.' in target_param_name:
            (parent_name, name) = target_param_name.rsplit('.', 1)
            parent = self.get_submodule(parent_name)
        else:
            name = target_param_name
            parent = self
        setattr(parent, name, source_param)
        self._adjust_bias(parent, source_param)
        if missing_keys is not None and remove_from_missing:
            missing_keys.discard(target_param_name)