def _sync_request():
    try:
        client = self._get_oci_client()
        response = client.chat(chat_details)
        return response
    except Exception as e:
        status_code = getattr(e, 'status', 500)
        if status_code == 429:
            raise ModelRateLimitError(message=f'Rate limit exceeded: {str(e)}', model=self.name) from e
        else:
            raise ModelProviderError(message=str(e), status_code=status_code, model=self.name) from e