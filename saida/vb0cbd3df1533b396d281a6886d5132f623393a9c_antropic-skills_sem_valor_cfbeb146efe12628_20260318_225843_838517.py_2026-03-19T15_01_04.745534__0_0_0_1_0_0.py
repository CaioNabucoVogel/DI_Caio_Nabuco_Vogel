def validate_file_against_xsd(self, xml_file, verbose=False):
    xml_file = Path(xml_file).resolve()
    unpacked_dir = self.unpacked_dir.resolve()
    (is_valid, current_errors) = self._validate_single_file_xsd(xml_file, unpacked_dir)
    if is_valid is None:
        return (None, set())
    elif is_valid:
        return (True, set())
    original_errors = self._get_original_file_errors(xml_file)
    assert current_errors is not None
    new_errors = current_errors - original_errors
    new_errors = {e for e in new_errors if not any((pattern in e for pattern in self.IGNORED_VALIDATION_ERRORS))}
    if new_errors:
        if verbose:
            relative_path = xml_file.relative_to(unpacked_dir)
            print(f'FAILED - {relative_path}: {len(new_errors)} new error(s)')
            for error in list(new_errors)[:3]:
                truncated = error[:250] + '...' if len(error) > 250 else error
                print(f'  - {truncated}')
        return (False, new_errors)
    else:
        if verbose:
            print(f'PASSED - No new errors (original had {len(current_errors)} errors)')
        return (True, set())