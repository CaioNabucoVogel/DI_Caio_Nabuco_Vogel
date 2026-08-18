def validate_file_references(self):
    errors = []
    rels_files = list(self.unpacked_dir.rglob('*.rels'))
    if not rels_files:
        if self.verbose:
            print('PASSED - No .rels files found')
        return True
    all_files = []
    for file_path in self.unpacked_dir.rglob('*'):
        if file_path.is_file() and file_path.name != '[Content_Types].xml' and (not file_path.name.endswith('.rels')):
            all_files.append(file_path.resolve())
    all_referenced_files = set()
    if self.verbose:
        print(f'Found {len(rels_files)} .rels files and {len(all_files)} target files')
    for rels_file in rels_files:
        try:
            rels_root = lxml.etree.parse(str(rels_file)).getroot()
            rels_dir = rels_file.parent
            referenced_files = set()
            broken_refs = []
            for rel in rels_root.findall('.//ns:Relationship', namespaces={'ns': self.PACKAGE_RELATIONSHIPS_NAMESPACE}):
                target = rel.get('Target')
                if target and (not target.startswith(('http', 'mailto:'))):
                    if target.startswith('/'):
                        target_path = self.unpacked_dir / target.lstrip('/')
                    elif rels_file.name == '.rels':
                        target_path = self.unpacked_dir / target
                    else:
                        base_dir = rels_dir.parent
                        target_path = base_dir / target
                    try:
                        target_path = target_path.resolve()
                        if target_path.exists() and target_path.is_file():
                            referenced_files.add(target_path)
                            all_referenced_files.add(target_path)
                        else:
                            broken_refs.append((target, rel.sourceline))
                    except (OSError, ValueError):
                        broken_refs.append((target, rel.sourceline))
            if broken_refs:
                rel_path = rels_file.relative_to(self.unpacked_dir)
                for (broken_ref, line_num) in broken_refs:
                    errors.append(f'  {rel_path}: Line {line_num}: Broken reference to {broken_ref}')
        except Exception as e:
            rel_path = rels_file.relative_to(self.unpacked_dir)
            errors.append(f'  Error parsing {rel_path}: {e}')
    unreferenced_files = set(all_files) - all_referenced_files
    if unreferenced_files:
        for unref_file in sorted(unreferenced_files):
            unref_rel_path = unref_file.relative_to(self.unpacked_dir)
            errors.append(f'  Unreferenced file: {unref_rel_path}')
    if errors:
        print(f'FAILED - Found {len(errors)} relationship validation errors:')
        for error in errors:
            print(error)
        print('CRITICAL: These errors will cause the document to appear corrupt. ' + 'Broken references MUST be fixed, ' + 'and unreferenced files MUST be referenced or removed.')
        return False
    else:
        if self.verbose:
            print('PASSED - All references are valid and all files are properly referenced')
        return True