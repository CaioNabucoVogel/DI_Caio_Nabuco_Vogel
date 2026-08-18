def validate_all_relationship_ids(self):
    import lxml.etree
    errors = []
    for xml_file in self.xml_files:
        if xml_file.suffix == '.rels':
            continue
        rels_dir = xml_file.parent / '_rels'
        rels_file = rels_dir / f'{xml_file.name}.rels'
        if not rels_file.exists():
            continue
        try:
            rels_root = lxml.etree.parse(str(rels_file)).getroot()
            rid_to_type = {}
            for rel in rels_root.findall(f'.//{{{self.PACKAGE_RELATIONSHIPS_NAMESPACE}}}Relationship'):
                rid = rel.get('Id')
                rel_type = rel.get('Type', '')
                if rid:
                    if rid in rid_to_type:
                        rels_rel_path = rels_file.relative_to(self.unpacked_dir)
                        errors.append(f"  {rels_rel_path}: Line {rel.sourceline}: Duplicate relationship ID '{rid}' (IDs must be unique)")
                    type_name = rel_type.split('/')[-1] if '/' in rel_type else rel_type
                    rid_to_type[rid] = type_name
            xml_root = lxml.etree.parse(str(xml_file)).getroot()
            r_ns = self.OFFICE_RELATIONSHIPS_NAMESPACE
            rid_attrs_to_check = ['id', 'embed', 'link']
            for elem in xml_root.iter():
                for attr_name in rid_attrs_to_check:
                    rid_attr = elem.get(f'{{{r_ns}}}{attr_name}')
                    if not rid_attr:
                        continue
                    xml_rel_path = xml_file.relative_to(self.unpacked_dir)
                    elem_name = elem.tag.split('}')[-1] if '}' in elem.tag else elem.tag
                    if rid_attr not in rid_to_type:
                        errors.append(f"  {xml_rel_path}: Line {elem.sourceline}: <{elem_name}> r:{attr_name} references non-existent relationship '{rid_attr}' (valid IDs: {', '.join(sorted(rid_to_type.keys())[:5])}{('...' if len(rid_to_type) > 5 else '')})")
                    elif attr_name == 'id' and self.ELEMENT_RELATIONSHIP_TYPES:
                        expected_type = self._get_expected_relationship_type(elem_name)
                        if expected_type:
                            actual_type = rid_to_type[rid_attr]
                            if expected_type not in actual_type.lower():
                                errors.append(f"  {xml_rel_path}: Line {elem.sourceline}: <{elem_name}> references '{rid_attr}' which points to '{actual_type}' but should point to a '{expected_type}' relationship")
        except Exception as e:
            xml_rel_path = xml_file.relative_to(self.unpacked_dir)
            errors.append(f'  Error processing {xml_rel_path}: {e}')
    if errors:
        print(f'FAILED - Found {len(errors)} relationship ID reference errors:')
        for error in errors:
            print(error)
        print('\nThese ID mismatches will cause the document to appear corrupt!')
        return False
    else:
        if self.verbose:
            print('PASSED - All relationship ID references are valid')
        return True