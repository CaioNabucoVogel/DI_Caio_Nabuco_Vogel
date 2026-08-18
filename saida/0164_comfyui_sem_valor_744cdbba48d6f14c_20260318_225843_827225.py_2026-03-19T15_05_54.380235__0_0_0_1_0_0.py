def process_full_path(full_path: str) -> FileInfo | str | list[str]:
    if full_info:
        return get_file_info(full_path, path)
    rel_path = os.path.relpath(full_path, path).replace(os.sep, '/')
    if split_path:
        return [rel_path] + rel_path.split('/')
    return rel_path