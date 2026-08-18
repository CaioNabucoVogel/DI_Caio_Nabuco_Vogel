def validate_xml(self):
    errors = []
    for xml_file in self.xml_files:
        try:
            lxml.etree.parse(str(xml_file))
        except lxml.etree.XMLSyntaxError as e:
            errors.append(f'  {xml_file.relative_to(self.unpacked_dir)}: Line {e.lineno}: {e.msg}')
        except Exception as e:
            errors.append(f'  {xml_file.relative_to(self.unpacked_dir)}: Unexpected error: {str(e)}')
    if errors:
        print(f'FAILED - Found {len(errors)} XML violations:')
        for error in errors:
            print(error)
        return False
    else:
        if self.verbose:
            print('PASSED - All XML files are well-formed')
        return True