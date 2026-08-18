@staticmethod
def validate_integration_method(invocation_context: ApiInvocationContext):
    if invocation_context.integration['httpMethod'] != HTTPMethod.POST:
        raise ApiGatewayIntegrationError('Internal server error', status_code=500)