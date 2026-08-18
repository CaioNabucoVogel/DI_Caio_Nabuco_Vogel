def validate_namespaces(self):
    errors = []
    for xml_file in self.xml_files:
        try:
            root = lxml.etree.parse(str(xml_file)).getroot()
            declared = set(root.nsmap.keys()) - {None}
            for attr_val in [v for (k, v) in root.attrib.items() if k.endswith('Ignorable')]:
                undeclared = set(attr_val.split()) - declared
                errors.extend((f"  {xml_file.relative_to(self.unpacked_dir)}: Namespace '{ns}' in Ignorable but not declared" for ns in undeclared))
        except lxml.etree.XMLSyntaxError:
            continue
    if errors:
        print(f'FAILED - {len(errors)} namespace issues:')
        for error in errors:
            print(error)
        return False
    if self.verbose:
        print('PASSED - All namespace prefixes properly declared')
    return True