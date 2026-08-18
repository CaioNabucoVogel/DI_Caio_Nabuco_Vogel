def _resize_screenshot(self, screenshot_b64: str) -> str:
    """Resize screenshot to llm_screenshot_size if configured."""
    if not self.llm_screenshot_size:
        return screenshot_b64
    try:
        import base64
        import logging
        from io import BytesIO
        from PIL import Image
        img = Image.open(BytesIO(base64.b64decode(screenshot_b64)))
        if img.size == self.llm_screenshot_size:
            return screenshot_b64
        logging.getLogger(__name__).info(f'🔄 Resizing screenshot from {img.size[0]}x{img.size[1]} to {self.llm_screenshot_size[0]}x{self.llm_screenshot_size[1]} for LLM')
        img_resized = img.resize(self.llm_screenshot_size, Image.Resampling.LANCZOS)
        buffer = BytesIO()
        img_resized.save(buffer, format='PNG')
        return base64.b64encode(buffer.getvalue()).decode('utf-8')
    except Exception as e:
        logging.getLogger(__name__).warning(f'Failed to resize screenshot: {e}, using original')
        return screenshot_b64