@classmethod
def update_content_length(cls, response: Response):
    if response and response.content is not None:
        response.headers['Content-Length'] = str(len(response.content))