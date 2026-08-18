def validate_unique_ids(self):
    errors = []
    global_ids = {}
    for xml_file in self.xml_files:
        try:
            root = lxml.etree.parse(str(xml_file)).getroot()
            file_ids = {}
            mc_elements = root.xpath('.//mc:AlternateContent', namespaces={'mc': self.MC_NAMESPACE})
            for elem in mc_elements:
                elem.getparent().remove(elem)
            for elem in root.iter():
                tag = elem.tag.split('}')[-1].lower() if '}' in elem.tag else elem.tag.lower()
                if tag in self.UNIQUE_ID_REQUIREMENTS:
                    in_excluded_container = any((ancestor.tag.split('}')[-1].lower() in self.EXCLUDED_ID_CONTAINERS for ancestor in elem.iterancestors()))
                    if in_excluded_container:
                        continue
                    (attr_name, scope) = self.UNIQUE_ID_REQUIREMENTS[tag]
                    id_value = None
                    for (attr, value) in elem.attrib.items():
                        attr_local = attr.split('}')[-1].lower() if '}' in attr else attr.lower()
                        if attr_local == attr_name:
                            id_value = value
                            break
                    if id_value is not None:
                        if scope == 'global':
                            if id_value in global_ids:
                                (prev_file, prev_line, prev_tag) = global_ids[id_value]
                                errors.append(f"  {xml_file.relative_to(self.unpacked_dir)}: Line {elem.sourceline}: Global ID '{id_value}' in <{tag}> already used in {prev_file} at line {prev_line} in <{prev_tag}>")
                            else:
                                global_ids[id_value] = (xml_file.relative_to(self.unpacked_dir), elem.sourceline, tag)
                        elif scope == 'file':
                            key = (tag, attr_name)
                            if key not in file_ids:
                                file_ids[key] = {}
                            if id_value in file_ids[key]:
                                prev_line = file_ids[key][id_value]
                                errors.append(f"  {xml_file.relative_to(self.unpacked_dir)}: Line {elem.sourceline}: Duplicate {attr_name}='{id_value}' in <{tag}> (first occurrence at line {prev_line})")
                            else:
                                file_ids[key][id_value] = elem.sourceline
        except (lxml.etree.XMLSyntaxError, Exception) as e:
            errors.append(f'  {xml_file.relative_to(self.unpacked_dir)}: Error: {e}')
    if errors:
        print(f'FAILED - Found {len(errors)} ID uniqueness violations:')
        for error in errors:
            print(error)
        return False
    else:
        if self.verbose:
            print('PASSED - All required IDs are unique')
        return True