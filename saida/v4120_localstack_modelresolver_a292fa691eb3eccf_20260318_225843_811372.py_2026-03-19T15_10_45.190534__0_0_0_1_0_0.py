def _remove_self_ref(self, resolved_schema: dict):
    for (key, value) in resolved_schema.items():
        if key == '$ref':
            ref_name = value.rsplit('/', maxsplit=1)[-1]
            if ref_name == self.model_name:
                resolved_schema[key] = '#'
        elif isinstance(value, dict):
            self._remove_self_ref(value)