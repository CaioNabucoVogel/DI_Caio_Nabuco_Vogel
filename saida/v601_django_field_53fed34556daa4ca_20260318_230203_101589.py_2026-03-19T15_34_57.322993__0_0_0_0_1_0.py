def has_changed(self, initial, data):
    """Return True if data differs from initial."""
    if self.disabled:
        return False
    try:
        data = self.to_python(data)
        if hasattr(self, '_coerce'):
            return self._coerce(data) != self._coerce(initial)
    except ValidationError:
        return True
    initial_value = initial if initial is not None else ''
    data_value = data if data is not None else ''
    return initial_value != data_value