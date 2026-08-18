def _cleanup_temp_dir(self, temp_dir: Path | str) -> None:
    """Clean up temporary directory.

		Args:
			temp_dir: Path to temporary directory to remove
		"""
    if not temp_dir:
        return
    try:
        temp_path = Path(temp_dir)
        if 'browseruse-tmp-' in str(temp_path):
            shutil.rmtree(temp_path, ignore_errors=True)
    except Exception as e:
        self.logger.debug(f'Failed to cleanup temp dir {temp_dir}: {e}')