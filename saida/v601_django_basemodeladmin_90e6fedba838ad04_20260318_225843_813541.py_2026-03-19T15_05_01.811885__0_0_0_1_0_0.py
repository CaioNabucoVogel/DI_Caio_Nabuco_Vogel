def lookup_allowed(self, lookup, value, request):
    from django.contrib.admin.filters import SimpleListFilter
    model = self.model
    for fk_lookup in model._meta.related_fkey_lookups:
        if callable(fk_lookup):
            fk_lookup = fk_lookup()
        if (lookup, value) in widgets.url_params_from_lookup_dict(fk_lookup).items():
            return True
    relation_parts = []
    prev_field = None
    parts = lookup.split(LOOKUP_SEP)
    for part in parts:
        try:
            field = model._meta.get_field(part)
        except FieldDoesNotExist:
            break
        if not prev_field or (prev_field.is_relation and field not in model._meta.parents.values() and (field is not model._meta.auto_field) and (model._meta.auto_field is None or part not in getattr(prev_field, 'to_fields', [])) and (field.is_relation or not field.primary_key)):
            relation_parts.append(part)
        if not getattr(field, 'path_infos', None):
            break
        prev_field = field
        model = field.path_infos[-1].to_opts.model
    if len(relation_parts) <= 1:
        return True
    valid_lookups = {self.date_hierarchy}
    for filter_item in self.get_list_filter(request):
        if isinstance(filter_item, type) and issubclass(filter_item, SimpleListFilter):
            valid_lookups.add(filter_item.parameter_name)
        elif isinstance(filter_item, (list, tuple)):
            valid_lookups.add(filter_item[0])
        else:
            valid_lookups.add(filter_item)
    return not {LOOKUP_SEP.join(relation_parts), LOOKUP_SEP.join([*relation_parts, part])}.isdisjoint(valid_lookups)