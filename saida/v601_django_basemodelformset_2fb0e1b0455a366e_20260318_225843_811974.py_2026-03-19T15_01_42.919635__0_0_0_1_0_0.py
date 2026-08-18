def get_queryset(self):
    if not hasattr(self, '_queryset'):
        if self.queryset is not None:
            qs = self.queryset
        else:
            qs = self.model._default_manager.get_queryset()
        if not qs.ordered:
            qs = qs.order_by(self.model._meta.pk.name)
        self._queryset = qs
    return self._queryset