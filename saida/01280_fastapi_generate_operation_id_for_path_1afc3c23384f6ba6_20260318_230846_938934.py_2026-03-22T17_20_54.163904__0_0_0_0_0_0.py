def generate_operation_id_for_path(*, name: str, path: str, method: str) -> str:
    warnings.warn(message='fastapi.utils.generate_operation_id_for_path() was deprecated, it is not used internally, and will be removed soon', category=FastAPIDeprecationWarning, stacklevel=2)
    operation_id = f'{name}{path}'
    operation_id = re.sub('\\W', '_', operation_id)
    operation_id = f'{operation_id}_{method.lower()}'
    return operation_id