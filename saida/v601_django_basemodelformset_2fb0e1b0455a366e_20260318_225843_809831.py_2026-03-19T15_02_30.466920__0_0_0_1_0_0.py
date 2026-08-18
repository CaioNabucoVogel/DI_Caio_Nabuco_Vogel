def save_existing_objects(self, commit=True):
    self.changed_objects = []
    self.deleted_objects = []
    if not self.initial_forms:
        return []
    saved_instances = []
    forms_to_delete = self.deleted_forms
    for form in self.initial_forms:
        obj = form.instance
        if not obj._is_pk_set():
            continue
        if form in forms_to_delete:
            self.deleted_objects.append(obj)
            self.delete_existing(obj, commit=commit)
        elif form.has_changed():
            self.changed_objects.append((obj, form.changed_data))
            saved_instances.append(self.save_existing(form, obj, commit=commit))
            if not commit:
                self.saved_forms.append(form)
    return saved_instances