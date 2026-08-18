def __init__(self, unpacked_dir, original_file=None, verbose=False):
    self.unpacked_dir = Path(unpacked_dir).resolve()
    self.original_file = Path(original_file) if original_file else None
    self.verbose = verbose
    self.schemas_dir = Path(__file__).parent.parent / 'schemas'
    patterns = ['*.xml', '*.rels']
    self.xml_files = [f for pattern in patterns for f in self.unpacked_dir.rglob(pattern)]
    if not self.xml_files:
        print(f'Warning: No XML files found in {self.unpacked_dir}')