def _construct_form(self, i, **kwargs):
    pk_required = i < self.initial_form_count()
    if pk_required:
        if self.is_bound:
            pk_key = '%s-%s' % (self.add_prefix(i), self.model._meta.pk.name)
            try:
                pk = self.data[pk_key]
            except KeyError:
                pass
            else:
                to_python = self._get_to_python(self.model._meta.pk)
                try:
                    pk = to_python(pk)
                except ValidationError:
                    pass
                else:
                    kwargs['instance'] = self._existing_object(pk)
        else:
            kwargs['instance'] = self.get_queryset()[i]
    elif self.initial_extra:
        try:
            kwargs['initial'] = self.initial_extra[i - self.initial_form_count()]
        except IndexError:
            pass
    form = super()._construct_form(i, **kwargs)
    if pk_required:
        form.fields[self.model._meta.pk.name].required = True
    return form