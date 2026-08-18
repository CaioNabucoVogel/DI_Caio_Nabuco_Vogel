def process_text_content(text, content_type):
    if not text:
        return text
    matches = list(template_pattern.finditer(text))
    if matches:
        for match in matches:
            warnings.append(f'Found template tag in {content_type}: {match.group()}')
        return template_pattern.sub('', text)
    return text