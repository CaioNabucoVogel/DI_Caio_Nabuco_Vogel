def __init__(self, *, required=True, widget=None, label=None, initial=None, help_text='', error_messages=None, show_hidden_initial=False, validators=(), localize=False, disabled=False, label_suffix=None, template_name=None, bound_field_class=None):
    (self.required, self.label, self.initial) = (required, label, initial)
    self.show_hidden_initial = show_hidden_initial
    self.help_text = help_text
    self.disabled = disabled
    self.label_suffix = label_suffix
    self.bound_field_class = bound_field_class or self.bound_field_class
    widget = widget or self.widget
    if isinstance(widget, type):
        widget = widget()
    else:
        widget = copy.deepcopy(widget)
    self.localize = localize
    if self.localize:
        widget.is_localized = True
    widget.is_required = self.required
    extra_attrs = self.widget_attrs(widget)
    if extra_attrs:
        widget.attrs.update(extra_attrs)
    self.widget = widget
    messages = {}
    for c in reversed(self.__class__.__mro__):
        messages.update(getattr(c, 'default_error_messages', {}))
    messages.update(error_messages or {})
    self.error_messages = messages
    self.validators = [*self.default_validators, *validators]
    self.template_name = template_name
    super().__init__()