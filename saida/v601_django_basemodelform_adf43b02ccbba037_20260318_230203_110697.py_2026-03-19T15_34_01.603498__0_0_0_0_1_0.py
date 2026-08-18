def save(self, commit=True):
    """
        Save this form's self.instance object if commit=True. Otherwise, add
        a save_m2m() method to the form which can be called after the instance
        is saved manually at a later time. Return the model instance.
        """
    if self.errors:
        raise ValueError("The %s could not be %s because the data didn't validate." % (self.instance._meta.object_name, 'created' if self.instance._state.adding else 'changed'))
    if commit:
        self.instance.save()
        self._save_m2m()
    else:
        self.save_m2m = self._save_m2m
    return self.instance