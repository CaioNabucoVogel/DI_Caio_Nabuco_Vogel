def _uses_cohere_format(self) -> bool:
    """Check if the provider uses Cohere chat request format."""
    return self.provider.lower() == 'cohere'