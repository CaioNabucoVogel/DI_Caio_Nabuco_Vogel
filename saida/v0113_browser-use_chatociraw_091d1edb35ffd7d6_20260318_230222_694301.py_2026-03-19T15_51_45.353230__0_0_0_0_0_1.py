def _extract_usage(self, response) -> ChatInvokeUsage | None:
    """Extract usage information from OCI response."""
    try:
        if hasattr(response, 'data') and hasattr(response.data, 'chat_response'):
            chat_response = response.data.chat_response
            if hasattr(chat_response, 'usage'):
                usage = chat_response.usage
                return ChatInvokeUsage(prompt_tokens=getattr(usage, 'prompt_tokens', 0), prompt_cached_tokens=None, prompt_cache_creation_tokens=None, prompt_image_tokens=None, completion_tokens=getattr(usage, 'completion_tokens', 0), total_tokens=getattr(usage, 'total_tokens', 0))
        return None
    except Exception:
        return None