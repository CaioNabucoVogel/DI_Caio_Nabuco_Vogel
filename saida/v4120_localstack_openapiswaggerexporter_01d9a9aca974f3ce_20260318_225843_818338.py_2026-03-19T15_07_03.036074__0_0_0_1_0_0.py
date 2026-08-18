def export(self, api_id: str, stage: str, export_format: str, with_extension: bool, account_id: str, region_name: str) -> str:
    """
        https://github.com/OAI/OpenAPI-Specification/blob/main/versions/2.0.md
        """
    apigateway_client = connect_to(aws_access_key_id=account_id, region_name=region_name).apigateway
    rest_api = apigateway_client.get_rest_api(restApiId=api_id)
    resources = apigateway_client.get_resources(restApiId=api_id)
    models = apigateway_client.get_models(restApiId=api_id)
    info = {}
    if (description := rest_api.get('description')) is not None:
        info['description'] = description
    spec = APISpec(title=rest_api.get('name'), version=rest_api.get('version') or timestamp(rest_api.get('createdDate'), format=TIMESTAMP_FORMAT_TZ), info=info, openapi_version=self.VERSION, basePath=f'/{stage}', schemes=['https'])
    self._add_paths(spec, resources, with_extension)
    self._add_models(spec, models['items'], '#/definitions')
    response = getattr(spec, self.export_formats.get(export_format))()
    if with_extension and isinstance(response, dict) and ((binary_media_types := rest_api.get('binaryMediaTypes')) is not None):
        response[OpenAPIExt.BINARY_MEDIA_TYPES] = binary_media_types
    return response