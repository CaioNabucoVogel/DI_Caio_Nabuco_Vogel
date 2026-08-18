def _preprocess_for_mc_ignorable(self, xml_doc):
    root = xml_doc.getroot()
    if f'{{{self.MC_NAMESPACE}}}Ignorable' in root.attrib:
        del root.attrib[f'{{{self.MC_NAMESPACE}}}Ignorable']
    return xml_doc