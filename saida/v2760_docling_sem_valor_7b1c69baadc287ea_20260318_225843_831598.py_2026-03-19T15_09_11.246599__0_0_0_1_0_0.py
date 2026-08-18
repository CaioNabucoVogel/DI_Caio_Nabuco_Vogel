def __init__(self, enabled: bool, artifacts_path: Optional[Path], accelerator_options: AcceleratorOptions, vlm_options: InlineVlmOptions):
    self.enabled = enabled
    self.vlm_options = vlm_options
    self.max_tokens = vlm_options.max_new_tokens
    self.temperature = vlm_options.temperature
    if self.enabled:
        try:
            from mlx_vlm import generate, load, stream_generate
            from mlx_vlm.prompt_utils import apply_chat_template
            from mlx_vlm.utils import load_config
        except ImportError:
            raise ImportError('mlx-vlm is not installed. Please install it via `pip install mlx-vlm` to use MLX VLM models.')
        repo_cache_folder = vlm_options.repo_id.replace('/', '--')
        self.apply_chat_template = apply_chat_template
        self.stream_generate = stream_generate
        if artifacts_path is None:
            artifacts_path = self.download_models(self.vlm_options.repo_id, revision=self.vlm_options.revision)
        elif (artifacts_path / repo_cache_folder).exists():
            artifacts_path = artifacts_path / repo_cache_folder
        else:
            available_models = []
            if artifacts_path.exists():
                available_models = [p.name for p in artifacts_path.iterdir() if p.is_dir()]
            raise FileNotFoundError(f"Model '{self.vlm_options.repo_id}' not found in artifacts_path.\nExpected location: {artifacts_path / repo_cache_folder}\nAvailable models in {artifacts_path}: {(', '.join(available_models) if available_models else 'none')}\n\nTo fix this issue:\n  1. Download the model: docling-tools models download-hf-repo {self.vlm_options.repo_id}\n  2. Or remove --artifacts-path to enable auto-download\n  3. Or use a different model that exists in your artifacts_path")
        (self.vlm_model, self.processor) = load(artifacts_path)
        self.config = load_config(artifacts_path)
        if self.vlm_options.custom_stopping_criteria:
            for criteria in self.vlm_options.custom_stopping_criteria:
                if isinstance(criteria, StoppingCriteria):
                    raise ValueError(f'MLX models do not support HuggingFace StoppingCriteria instances. Found {type(criteria).__name__}. Use GenerationStopper instead.')
                elif isinstance(criteria, type) and issubclass(criteria, StoppingCriteria):
                    raise ValueError(f'MLX models do not support HuggingFace StoppingCriteria classes. Found {criteria.__name__}. Use GenerationStopper instead.')