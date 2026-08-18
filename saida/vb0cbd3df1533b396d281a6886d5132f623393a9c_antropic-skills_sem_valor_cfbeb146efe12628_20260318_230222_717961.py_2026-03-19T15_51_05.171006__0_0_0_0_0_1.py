def _remove_template_tags_from_text_nodes(self, xml_doc):
    warnings = []
    template_pattern = re.compile('\\{\\{[^}]*\\}\\}')
    xml_string = lxml.etree.tostring(xml_doc, encoding='unicode')
    xml_copy = lxml.etree.fromstring(xml_string)

    def process_text_content(text, content_type):
        if not text:
            return text
        matches = list(template_pattern.finditer(text))
        if matches:
            for match in matches:
                warnings.append(f'Found template tag in {content_type}: {match.group()}')
            return template_pattern.sub('', text)
        return text
    for elem in xml_copy.iter():
        if not hasattr(elem, 'tag') or callable(elem.tag):
            continue
        tag_str = str(elem.tag)
        if tag_str.endswith('}t') or tag_str == 't':
            continue
        elem.text = process_text_content(elem.text, 'text content')
        elem.tail = process_text_content(elem.tail, 'tail content')
    return (lxml.etree.ElementTree(xml_copy), warnings)