class ResponseTemplates(Templates):
    """
    Handles response template rendering. The integration response status code is used to select
    the correct template to render, if there is no template for the status code, the default
    template is used.
    """

    def render(self, api_context: ApiInvocationContext, **kwargs) -> bytes | str:
        data = kwargs.get('response', '')
        response = data or api_context.response
        integration = api_context.integration
        api_context.data = response._content
        status_code = str(response.status_code)
        integration_responses = integration.get('integrationResponses')
        if not integration_responses:
            return response._content
        integration_status_codes = [str(code) for code in list(integration_responses.keys())]
        if not integration_status_codes:
            return response.content
        match_resp = status_code
        if isinstance(try_json(response._content), dict):
            resp_dict = try_json(response._content)
            if 'errorMessage' in resp_dict:
                match_resp = resp_dict.get('errorMessage')
        selected_integration_response = select_integration_response(match_resp, api_context)
        response.status_code = int(selected_integration_response.get('statusCode', 200))
        response_templates = selected_integration_response.get('responseTemplates', {})
        accept = api_context.headers.get('accept', APPLICATION_JSON)
        supported_types = [APPLICATION_JSON, APPLICATION_XML]
        media_type = accept if accept in supported_types else APPLICATION_JSON
        if not (template := response_templates.get(media_type, {})):
            return response._content
        variables = self.build_variables_mapping(api_context)
        response._content = self._render_as_text(template, variables)
        if media_type == APPLICATION_JSON:
            self._validate_json(response.content)
        elif media_type == APPLICATION_XML:
            self._validate_xml(response.content)
        if (response_overrides := variables.get('context', {}).get('responseOverride', {})):
            response.headers.update(response_overrides.get('header', {}).items())
            response.status_code = response_overrides.get('status', 200)
        LOG.debug('Endpoint response body after transformations:\n%s', response._content)
        return response._content

    def _render_as_text(self, template: str, variables: dict[str, Any]) -> str:
        """
        Render the given Velocity template string + variables into a plain string.
        :return: the template rendering result as a string
        """
        rendered_tpl = self.render_vtl(template, variables=variables)
        return rendered_tpl.strip()

    @staticmethod
    def _validate_json(content: str):
        """
        Checks that the content received is a valid JSON.
        :raise JSONDecodeError: if content is not valid JSON
        """
        try:
            json.loads(content)
        except Exception as e:
            LOG.info('Unable to parse template result as JSON: %s - %s', e, content)
            raise

    @staticmethod
    def _validate_xml(content: str):
        """
        Checks that the content received is a valid XML.
        :raise xml.parsers.expat.ExpatError: if content is not valid XML
        """
        try:
            xmltodict.parse(content)
        except Exception as e:
            LOG.info('Unable to parse template result as XML: %s - %s', e, content)
            raise