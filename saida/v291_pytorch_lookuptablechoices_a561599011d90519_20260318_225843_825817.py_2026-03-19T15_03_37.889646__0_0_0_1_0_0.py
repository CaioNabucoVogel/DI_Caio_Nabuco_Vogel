def _get_lookup_table(self) -> dict[str, list[dict[str, Any]]]:
    """
        Get the template lookup table from config.
        Override this method to use custom lookup table sources (database, API, etc.).
        """
    if not torch.cuda.is_available() or config.lookup_table.table is None:
        return {}
    return config.lookup_table.table