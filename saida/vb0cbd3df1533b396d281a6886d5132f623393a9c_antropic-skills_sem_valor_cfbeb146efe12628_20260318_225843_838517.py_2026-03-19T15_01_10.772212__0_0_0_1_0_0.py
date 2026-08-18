def _validate_single_file_xsd(self, xml_file, base_path):
    schema_path = self._get_schema_path(xml_file)
    if not schema_path:
        return (None, None)
    try:
        with open(schema_path, 'rb') as xsd_file:
            parser = lxml.etree.XMLParser()
            xsd_doc = lxml.etree.parse(xsd_file, parser=parser, base_url=str(schema_path))
            schema = lxml.etree.XMLSchema(xsd_doc)
        with open(xml_file, 'r') as f:
            xml_doc = lxml.etree.parse(f)
        (xml_doc, _) = self._remove_template_tags_from_text_nodes(xml_doc)
        xml_doc = self._preprocess_for_mc_ignorable(xml_doc)
        relative_path = xml_file.relative_to(base_path)
        if relative_path.parts and relative_path.parts[0] in self.MAIN_CONTENT_FOLDERS:
            xml_doc = self._clean_ignorable_namespaces(xml_doc)
        if schema.validate(xml_doc):
            return (True, set())
        else:
            errors = set()
            for error in schema.error_log:
                errors.add(error.message)
            return (False, errors)
    except Exception as e:
        return (False, {str(e)})