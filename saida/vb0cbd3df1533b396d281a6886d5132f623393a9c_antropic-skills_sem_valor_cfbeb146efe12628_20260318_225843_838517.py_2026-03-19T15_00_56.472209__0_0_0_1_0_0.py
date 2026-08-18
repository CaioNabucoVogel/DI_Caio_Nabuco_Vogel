def repair_whitespace_preservation(self) -> int:
    repairs = 0
    for xml_file in self.xml_files:
        try:
            content = xml_file.read_text(encoding='utf-8')
            dom = defusedxml.minidom.parseString(content)
            modified = False
            for elem in dom.getElementsByTagName('*'):
                if elem.tagName.endswith(':t') and elem.firstChild:
                    text = elem.firstChild.nodeValue
                    if text and (text.startswith((' ', '\t')) or text.endswith((' ', '\t'))):
                        if elem.getAttribute('xml:space') != 'preserve':
                            elem.setAttribute('xml:space', 'preserve')
                            text_preview = repr(text[:30]) + '...' if len(text) > 30 else repr(text)
                            print(f"  Repaired: {xml_file.name}: Added xml:space='preserve' to {elem.tagName}: {text_preview}")
                            repairs += 1
                            modified = True
            if modified:
                xml_file.write_bytes(dom.toxml(encoding='UTF-8'))
        except Exception:
            pass
    return repairs