def __init__(self, enabled: bool, artifacts_path: Optional[Path], options: DocumentPictureClassifierOptions, accelerator_options: AcceleratorOptions, enable_remote_services: bool=False):
    """
        Initializes the DocumentPictureClassifier.

        Parameters
        ----------
        enabled : bool
            Indicates whether the classifier is enabled.
        artifacts_path : Optional[Union[Path, str]],
            Path to the directory containing model artifacts.
        options : DocumentPictureClassifierOptions
            Configuration options for the classifier.
        accelerator_options : AcceleratorOptions
            Options for configuring the device and parallelism.
        """
    self.enabled = enabled
    self.options = options
    self.engine: Optional[BaseImageClassificationEngine] = None
    self._classes: dict[int, str] = {}
    if self.enabled:
        self.engine = create_image_classification_engine(options=self.options.engine_options, model_spec=self.options.model_spec, artifacts_path=artifacts_path, enable_remote_services=enable_remote_services, accelerator_options=accelerator_options)
        self.engine.initialize()
        self._classes = self.engine.get_label_mapping()