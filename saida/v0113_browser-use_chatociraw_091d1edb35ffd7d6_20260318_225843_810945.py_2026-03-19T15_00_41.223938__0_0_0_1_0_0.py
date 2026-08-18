def _get_supported_parameters(self) -> dict[str, bool]:
    """Get which parameters are supported by the current provider."""
    provider = self.provider.lower()
    if provider == 'meta':
        return {'temperature': True, 'max_tokens': True, 'frequency_penalty': True, 'presence_penalty': True, 'top_p': True, 'top_k': False}
    elif provider == 'cohere':
        return {'temperature': True, 'max_tokens': True, 'frequency_penalty': True, 'presence_penalty': False, 'top_p': True, 'top_k': True}
    elif provider == 'xai':
        return {'temperature': True, 'max_tokens': True, 'frequency_penalty': False, 'presence_penalty': False, 'top_p': True, 'top_k': True}
    else:
        return {'temperature': True, 'max_tokens': True, 'frequency_penalty': True, 'presence_penalty': True, 'top_p': True, 'top_k': True}