def generate(self, existing_ids: ExistingIds=None, tags: Tags=None, next_version: int=None) -> int:
    return int(generate_layer_version(self, next_version=next_version))