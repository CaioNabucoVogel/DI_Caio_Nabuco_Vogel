@staticmethod
def _is_base64_image(url: str) -> bool:
    """Check if the URL is a base64 encoded image."""
    return url.startswith('data:image/')