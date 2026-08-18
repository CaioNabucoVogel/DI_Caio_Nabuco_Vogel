def validate_content_types(self):
    errors = []
    content_types_file = self.unpacked_dir / '[Content_Types].xml'
    if not content_types_file.exists():
        print('FAILED - [Content_Types].xml file not found')
        return False
    try:
        root = lxml.etree.parse(str(content_types_file)).getroot()
        declared_parts = set()
        declared_extensions = set()
        for override in root.findall(f'.//{{{self.CONTENT_TYPES_NAMESPACE}}}Override'):
            part_name = override.get('PartName')
            if part_name is not None:
                declared_parts.add(part_name.lstrip('/'))
        for default in root.findall(f'.//{{{self.CONTENT_TYPES_NAMESPACE}}}Default'):
            extension = default.get('Extension')
            if extension is not None:
                declared_extensions.add(extension.lower())
        declarable_roots = {'sld', 'sldLayout', 'sldMaster', 'presentation', 'document', 'workbook', 'worksheet', 'theme'}
        media_extensions = {'png': 'image/png', 'jpg': 'image/jpeg', 'jpeg': 'image/jpeg', 'gif': 'image/gif', 'bmp': 'image/bmp', 'tiff': 'image/tiff', 'wmf': 'image/x-wmf', 'emf': 'image/x-emf'}
        all_files = list(self.unpacked_dir.rglob('*'))
        all_files = [f for f in all_files if f.is_file()]
        for xml_file in self.xml_files:
            path_str = str(xml_file.relative_to(self.unpacked_dir)).replace('\\', '/')
            if any((skip in path_str for skip in ['.rels', '[Content_Types]', 'docProps/', '_rels/'])):
                continue
            try:
                root_tag = lxml.etree.parse(str(xml_file)).getroot().tag
                root_name = root_tag.split('}')[-1] if '}' in root_tag else root_tag
                if root_name in declarable_roots and path_str not in declared_parts:
                    errors.append(f'  {path_str}: File with <{root_name}> root not declared in [Content_Types].xml')
            except Exception:
                continue
        for file_path in all_files:
            if file_path.suffix.lower() in {'.xml', '.rels'}:
                continue
            if file_path.name == '[Content_Types].xml':
                continue
            if '_rels' in file_path.parts or 'docProps' in file_path.parts:
                continue
            extension = file_path.suffix.lstrip('.').lower()
            if extension and extension not in declared_extensions:
                if extension in media_extensions:
                    relative_path = file_path.relative_to(self.unpacked_dir)
                    errors.append(f'''  {relative_path}: File with extension '{extension}' not declared in [Content_Types].xml - should add: <Default Extension="{extension}" ContentType="{media_extensions[extension]}"/>''')
    except Exception as e:
        errors.append(f'  Error parsing [Content_Types].xml: {e}')
    if errors:
        print(f'FAILED - Found {len(errors)} content type declaration errors:')
        for error in errors:
            print(error)
        return False
    else:
        if self.verbose:
            print('PASSED - All content files are properly declared in [Content_Types].xml')
        return True