@classmethod
def construct_invocation_event(cls, method, path, headers, data, query_string_params=None, is_base64_encoded=False):
    query_string_params = query_string_params or parse_request_data(method, path, '')
    single_value_query_string_params = {k: v[-1] if isinstance(v, list) else v for (k, v) in query_string_params.items()}
    to_capitalize: list[str] = ['authorization']
    headers = {k.capitalize() if k.lower() in to_capitalize else k: v for (k, v) in headers.items()}
    headers = canonicalize_headers(headers)
    return {'path': '/' + path.lstrip('/'), 'headers': headers, 'multiValueHeaders': multi_value_dict_for_list(headers), 'body': data, 'isBase64Encoded': is_base64_encoded, 'httpMethod': method, 'queryStringParameters': single_value_query_string_params or None, 'multiValueQueryStringParameters': dict_multi_values(query_string_params) or None}