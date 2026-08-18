def __init__(self, *, enabled: bool, enable_remote_services: bool, artifacts_path: Optional[Union[Path, str]], options: PictureDescriptionBaseOptions, accelerator_options: AcceleratorOptions):
    self.enabled = enabled
    self.options = options
    self.provenance = 'not-implemented'