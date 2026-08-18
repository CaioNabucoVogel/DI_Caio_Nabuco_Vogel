def as_sql(self, compiler, connection):
    connection.ops.check_expression_support(self)
    val = self.value
    output_field = self._output_field_or_none
    if output_field is not None:
        if self.for_save:
            val = output_field.get_db_prep_save(val, connection=connection)
        else:
            val = output_field.get_db_prep_value(val, connection=connection)
        if hasattr(output_field, 'get_placeholder'):
            return (output_field.get_placeholder(val, compiler, connection), [val])
    if val is None:
        return ('NULL', [])
    return ('%s', [val])