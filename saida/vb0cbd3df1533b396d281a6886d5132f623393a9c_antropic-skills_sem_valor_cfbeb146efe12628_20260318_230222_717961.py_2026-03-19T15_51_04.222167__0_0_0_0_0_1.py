def _get_original_file_errors(self, xml_file):
    if self.original_file is None:
        return set()
    import tempfile
    import zipfile
    xml_file = Path(xml_file).resolve()
    unpacked_dir = self.unpacked_dir.resolve()
    relative_path = xml_file.relative_to(unpacked_dir)
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        with zipfile.ZipFile(self.original_file, 'r') as zip_ref:
            zip_ref.extractall(temp_path)
        original_xml_file = temp_path / relative_path
        if not original_xml_file.exists():
            return set()
        (is_valid, errors) = self._validate_single_file_xsd(original_xml_file, temp_path)
        return errors if errors else set()