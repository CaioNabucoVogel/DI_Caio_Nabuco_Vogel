def _get_schema_path(self, xml_file):
    if xml_file.name in self.SCHEMA_MAPPINGS:
        return self.schemas_dir / self.SCHEMA_MAPPINGS[xml_file.name]
    if xml_file.suffix == '.rels':
        return self.schemas_dir / self.SCHEMA_MAPPINGS['.rels']
    if 'charts/' in str(xml_file) and xml_file.name.startswith('chart'):
        return self.schemas_dir / self.SCHEMA_MAPPINGS['chart']
    if 'theme/' in str(xml_file) and xml_file.name.startswith('theme'):
        return self.schemas_dir / self.SCHEMA_MAPPINGS['theme']
    if xml_file.parent.name in self.MAIN_CONTENT_FOLDERS:
        return self.schemas_dir / self.SCHEMA_MAPPINGS[xml_file.parent.name]
    return None