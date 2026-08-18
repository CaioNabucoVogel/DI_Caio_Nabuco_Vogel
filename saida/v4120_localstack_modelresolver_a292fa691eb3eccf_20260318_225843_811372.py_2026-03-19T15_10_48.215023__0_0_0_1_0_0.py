def get_resolved_model(self) -> dict | None:
    if not (resolved_model := self.rest_api_container.resolved_models.get(self.model_name)):
        model = self.rest_api_container.models.get(self.model_name)
        if not model:
            return None
        schema = json.loads(model['schema'])
        resolved_model = self.resolve_model(schema)
        if not resolved_model:
            return None
        if self._deps:
            resolved_model['$defs'] = self._deps
        self.rest_api_container.resolved_models[self.model_name] = resolved_model
    return resolved_model