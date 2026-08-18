def _update_errors(self, errors):
    opts = self._meta
    if hasattr(errors, 'error_dict'):
        error_dict = errors.error_dict
    else:
        error_dict = {NON_FIELD_ERRORS: errors}
    for (field, messages) in error_dict.items():
        if field == NON_FIELD_ERRORS and opts.error_messages and (NON_FIELD_ERRORS in opts.error_messages):
            error_messages = opts.error_messages[NON_FIELD_ERRORS]
        elif field in self.fields:
            error_messages = self.fields[field].error_messages
        else:
            continue
        for message in messages:
            if isinstance(message, ValidationError) and message.code in error_messages:
                message.message = error_messages[message.code]
    self.add_error(None, errors)