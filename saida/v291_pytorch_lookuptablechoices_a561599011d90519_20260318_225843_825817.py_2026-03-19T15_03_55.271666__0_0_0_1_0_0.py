def _finalize_template_configs(self, template_choices: dict[str, Generator[KernelTemplateChoice, None, None]], kernel_inputs: KernelInputs, templates: list[Union[KernelTemplate, ExternKernelChoice]], op_name: str, kwarg_overrides: Optional[dict[str, dict[str, Any]]]=None) -> list[KernelTemplateChoice]:
    """Check lookup table for hits, use those if found, otherwise fall back to parent."""
    template_uids = [template.uid for template in templates]
    template_hash_map = {}
    for template in templates:
        src_hash = getattr(template, 'src_hash', None)
        template_hash_map[template.uid] = src_hash
    log.debug('Choices: attempting lookup for %s with %d templates', op_name, len(template_uids))
    lookup_results = self.lookup_template_configs(kernel_inputs, op_name, template_uids, template_hash_map)
    if not lookup_results:
        log.info('LookupChoices: lookup miss for %s, using fallback', op_name)
        return self._fallback(template_choices, kernel_inputs, templates, op_name, kwarg_overrides)
    log.info('LookupChoices: lookup hit for %s - found %d/%d templates: %s', op_name, len(lookup_results), len(template_uids), list(lookup_results.keys()))
    return self._create_lookup_choices(lookup_results, templates, kernel_inputs, op_name)