def resolve_model(self, model: dict) -> dict | None:
    resolved_model = copy.deepcopy(model)
    model_names = set()

    def _look_for_ref(sub_model):
        for (key, value) in sub_model.items():
            if key == '$ref':
                ref_name = value.rsplit('/', maxsplit=1)[-1]
                if ref_name == self.model_name:
                    sub_model[key] = '#'
                    continue
                sub_model[key] = f'#/$defs/{ref_name}'
                if ref_name != self._current_resolving_name:
                    model_names.add(ref_name)
            elif isinstance(value, dict):
                _look_for_ref(value)
            elif isinstance(value, list):
                for val in value:
                    if isinstance(val, dict):
                        _look_for_ref(val)
    if isinstance(resolved_model, dict):
        _look_for_ref(resolved_model)
    if model_names:
        for ref_model_name in model_names:
            if ref_model_name in self._deps:
                continue
            (def_resolved, was_resolved) = self._get_resolved_submodel(model_name=ref_model_name)
            if not def_resolved:
                LOG.debug('Failed to resolve submodel %s for model %s', ref_model_name, self._current_resolving_name)
                return
            if was_resolved:
                def_resolved = copy.deepcopy(def_resolved)
            self._remove_self_ref(def_resolved)
            if '$deps' in def_resolved:
                def_resolved['$defs'].pop(self.model_name, None)
                def_resolved_defs = def_resolved.pop('$defs')
                self._deps.update(def_resolved_defs)
            self._deps[ref_model_name] = def_resolved
    return resolved_model