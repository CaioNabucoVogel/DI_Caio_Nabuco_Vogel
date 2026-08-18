def validate_against_xsd(self):
    new_errors = []
    original_error_count = 0
    valid_count = 0
    skipped_count = 0
    for xml_file in self.xml_files:
        relative_path = str(xml_file.relative_to(self.unpacked_dir))
        (is_valid, new_file_errors) = self.validate_file_against_xsd(xml_file, verbose=False)
        if is_valid is None:
            skipped_count += 1
            continue
        elif is_valid and (not new_file_errors):
            valid_count += 1
            continue
        elif is_valid:
            original_error_count += 1
            valid_count += 1
            continue
        new_errors.append(f'  {relative_path}: {len(new_file_errors)} new error(s)')
        for error in list(new_file_errors)[:3]:
            new_errors.append(f'    - {error[:250]}...' if len(error) > 250 else f'    - {error}')
    if self.verbose:
        print(f'Validated {len(self.xml_files)} files:')
        print(f'  - Valid: {valid_count}')
        print(f'  - Skipped (no schema): {skipped_count}')
        if original_error_count:
            print(f'  - With original errors (ignored): {original_error_count}')
        print(f"  - With NEW errors: {len(new_errors) > 0 and len([e for e in new_errors if not e.startswith('    ')]) or 0}")
    if new_errors:
        print('\nFAILED - Found NEW validation errors:')
        for error in new_errors:
            print(error)
        return False
    else:
        if self.verbose:
            print('\nPASSED - No new XSD validation errors introduced')
        return True