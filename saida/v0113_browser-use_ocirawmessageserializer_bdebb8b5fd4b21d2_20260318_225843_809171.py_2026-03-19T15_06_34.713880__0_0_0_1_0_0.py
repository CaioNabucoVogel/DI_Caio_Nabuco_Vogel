@staticmethod
def _create_image_content(part: ContentPartImageParam) -> ImageContent:
    """Convert ContentPartImageParam to OCI ImageContent."""
    url = part.image_url.url
    if OCIRawMessageSerializer._is_base64_image(url):
        image_url = ImageUrl(url=url)
    else:
        image_url = ImageUrl(url=url)
    return ImageContent(image_url=image_url)