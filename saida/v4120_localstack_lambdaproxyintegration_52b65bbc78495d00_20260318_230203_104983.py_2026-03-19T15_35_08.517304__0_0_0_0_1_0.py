@classmethod
def process_apigateway_invocation(cls, func_arn, path, payload, invocation_context: ApiInvocationContext, query_string_params=None) -> str:
    if (path_params := invocation_context.path_params) is None:
        path_params = {}
    if (request_context := invocation_context.context) is None:
        request_context = {}
    try:
        resource_path = invocation_context.resource_path or path
        event = cls.construct_invocation_event(invocation_context.method, path, invocation_context.headers, payload, query_string_params, invocation_context.is_data_base64_encoded)
        path_params = dict(path_params)
        cls.fix_proxy_path_params(path_params)
        event['pathParameters'] = path_params
        event['resource'] = resource_path
        event['requestContext'] = request_context
        event['stageVariables'] = invocation_context.stage_variables
        LOG.debug('Running Lambda function %s from API Gateway invocation: %s %s', func_arn, invocation_context.method or 'GET', path)
        asynchronous = invocation_context.headers.get('X-Amz-Invocation-Type') == "'Event'"
        return call_lambda(function_arn=func_arn, event=to_bytes(json.dumps(event)), asynchronous=asynchronous, invocation_context=invocation_context)
    except ClientError as e:
        raise IntegrationAccessError() from e
    except Exception as e:
        LOG.warning('Unable to run Lambda function on API Gateway message: %s', e)