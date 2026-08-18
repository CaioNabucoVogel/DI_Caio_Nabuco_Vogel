def __init__(self, rest_api_container: RestApiContainer, model_name: str):
    self.rest_api_container = rest_api_container
    self.model_name = model_name
    self._deps = {}
    self._current_resolving_name = None