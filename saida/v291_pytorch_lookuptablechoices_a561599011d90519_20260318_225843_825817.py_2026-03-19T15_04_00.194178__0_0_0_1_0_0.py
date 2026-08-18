def _create_lookup_choices(self, lookup_results: dict[str, list[dict[str, Any]]], templates: list[Union[KernelTemplate, ExternKernelChoice]], kernel_inputs: KernelInputs, op_name: str) -> list[KernelTemplateChoice]:
    """Create KernelTemplateChoice objects from lookup results using parent's get_ktc method."""
    templates_by_uid = {template.uid: template for template in templates}
    lookup_choices: list[KernelTemplateChoice] = []
    for (template_uid, configs) in lookup_results.items():
        template = templates_by_uid[template_uid]
        ktc_generator = self.get_ktc(kernel_inputs, template, op_name)
        try:
            base_ktc = next(ktc_generator)
        except StopIteration:
            continue
        for c in configs:
            lookup_ktc = KernelTemplateChoice(template=base_ktc.template, params=DictKernelTemplateParams(c), extra_kwargs=base_ktc.extra_kwargs, layout=base_ktc.layout, inputs=base_ktc.inputs)
            lookup_choices.append(lookup_ktc)
    return lookup_choices