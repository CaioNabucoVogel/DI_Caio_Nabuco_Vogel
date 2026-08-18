def create_model_field(name: str, type_: Any, class_validators: Optional[dict[str, Validator]]=None, default: Optional[Any]=Undefined, required: Union[bool, UndefinedType]=Undefined, model_config: Union[type[BaseConfig], None]=None, field_info: Optional[FieldInfo]=None, alias: Optional[str]=None, mode: Literal['validation', 'serialization']='validation', version: Literal['1', 'auto']='auto') -> ModelField:
    if annotation_is_pydantic_v1(type_):
        raise PydanticV1NotSupportedError(f'pydantic.v1 models are no longer supported by FastAPI. Please update the response model {type_!r}.')
    class_validators = class_validators or {}
    field_info = field_info or FieldInfo(annotation=type_, default=default, alias=alias)
    kwargs = {'mode': mode, 'name': name, 'field_info': field_info}
    try:
        return v2.ModelField(**kwargs)
    except PydanticSchemaGenerationError:
        raise fastapi.exceptions.FastAPIError(_invalid_args_message.format(type_=type_)) from None