def __init__(self, name: str, grid: Any, source: str, debug=False, cache_codegen_enabled_for_template=False, prologue_loads_all_inputs=False) -> None:
    super().__init__(name, hash=hashlib.sha256(source.encode('utf-8')).hexdigest())
    self.grid = grid
    self.template = self._template_from_string(source)
    assert name not in self.all_templates, 'duplicate template name'
    TritonTemplate.all_templates[name] = self
    self.debug = debug
    self._cache_codegen_enabled_for_template = cache_codegen_enabled_for_template
    self._generated_code_cache: GeneratedCodeCache = GeneratedCodeCache()
    clear_on_fresh_cache(self._generated_code_cache)
    self.prologue_loads_all_inputs = prologue_loads_all_inputs