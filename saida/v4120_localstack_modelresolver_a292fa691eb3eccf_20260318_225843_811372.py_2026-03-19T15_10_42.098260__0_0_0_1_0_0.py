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