def _resolve_and_populate_arg(self, arg_name, call_spec, call_context, kwargs):
    if arg_name in call_spec.user_arguments_dict:
        value = call_spec.user_arguments_dict[arg_name]
    elif call_context.get_value(arg_name) is not None:
        value = call_context.get_value(arg_name)
    else:
        value = call_spec.arguments_dict.get(arg_name, None)
    call_context.set_value(arg_name, value)
    if self._call_has_context_arg.get(arg_name, False) and value is not None:
        kwargs[arg_name] = value