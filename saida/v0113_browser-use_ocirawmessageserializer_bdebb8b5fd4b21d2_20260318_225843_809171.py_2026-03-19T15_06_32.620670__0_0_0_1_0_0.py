@staticmethod
def _parse_base64_url(url: str) -> str:
    """Parse base64 URL and return the base64 data."""
    if not OCIRawMessageSerializer._is_base64_image(url):
        raise ValueError(f'Not a base64 image URL: {url}')
    try:
        (header, data) = url.split(',', 1)
        return data
    except ValueError:
        raise ValueError(f'Invalid base64 image URL format: {url}')