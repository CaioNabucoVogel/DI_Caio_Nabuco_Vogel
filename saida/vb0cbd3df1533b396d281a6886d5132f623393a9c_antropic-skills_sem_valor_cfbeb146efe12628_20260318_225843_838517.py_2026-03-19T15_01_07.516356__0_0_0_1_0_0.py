def _clean_ignorable_namespaces(self, xml_doc):
    xml_string = lxml.etree.tostring(xml_doc, encoding='unicode')
    xml_copy = lxml.etree.fromstring(xml_string)
    for elem in xml_copy.iter():
        attrs_to_remove = []
        for attr in elem.attrib:
            if '{' in attr:
                ns = attr.split('}')[0][1:]
                if ns not in self.OOXML_NAMESPACES:
                    attrs_to_remove.append(attr)
        for attr in attrs_to_remove:
            del elem.attrib[attr]
    self._remove_ignorable_elements(xml_copy)
    return lxml.etree.ElementTree(xml_copy)