def __init__(self, data=None, files=None, auto_id='id_%s', prefix=None, initial=None, error_class=ErrorList, label_suffix=None, empty_permitted=False, instance=None, use_required_attribute=None, renderer=None):
    opts = self._meta
    if opts.model is None:
        raise ValueError('ModelForm has no model class specified.')
    if instance is None:
        self.instance = opts.model()
        object_data = {}
    else:
        self.instance = instance
        object_data = model_to_dict(instance, opts.fields, opts.exclude)
    if initial is not None:
        object_data.update(initial)
    self._validate_unique = False
    self._validate_constraints = False
    super().__init__(data, files, auto_id, prefix, object_data, error_class, label_suffix, empty_permitted, use_required_attribute=use_required_attribute, renderer=renderer)
    for formfield in self.fields.values():
        apply_limit_choices_to_to_formfield(formfield)