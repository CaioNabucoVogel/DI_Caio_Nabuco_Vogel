def _get_resolved_submodel(self, model_name: str) -> tuple[dict | None, bool | None]:
    was_resolved = True
    if not (resolved_model := self.rest_api_container.resolved_models.get(model_name)):
        was_resolved = False
        model = self.rest_api_container.models.get(model_name)
        if not model:
            LOG.warning("Error while validating the request body, could not the find the Model: '%s'", model_name)
            return (None, was_resolved)
        schema = json.loads(model['schema'])
        with self._resolving_ctx(model_name):
            resolved_model = self.resolve_model(schema)
    return (resolved_model, was_resolved)