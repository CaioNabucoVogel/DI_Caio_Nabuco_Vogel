def save_new_objects(self, commit=True):
    self.new_objects = []
    for form in self.extra_forms:
        if not form.has_changed():
            continue
        if self.can_delete and self._should_delete_form(form):
            continue
        self.new_objects.append(self.save_new(form, commit=commit))
        if not commit:
            self.saved_forms.append(form)
    return self.new_objects