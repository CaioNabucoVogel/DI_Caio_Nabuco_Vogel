def __init__(self, enabled: bool, artifacts_path: Optional[Path], accelerator_options: AcceleratorOptions, vlm_options: InlineVlmOptions):
    self.enabled = enabled
    self.vlm_options: InlineVlmOptions = vlm_options
    self.llm = None
    self.sampling_params = None
    self.processor = None
    self.device = 'cpu'
    self.max_new_tokens = vlm_options.max_new_tokens
    self.temperature = vlm_options.temperature
    if not self.enabled:
        return
    from transformers import AutoProcessor
    try:
        from vllm import LLM, SamplingParams
    except ImportError:
        if sys.version_info < (3, 14):
            raise ImportError('vllm is not installed. Please install it via `pip install vllm`.')
        else:
            raise ImportError('vllm is not installed. It is not yet available on Python 3.14.')
    self.device = decide_device(accelerator_options.device, supported_devices=vlm_options.supported_devices)
    _log.debug(f'Available device for VLM: {self.device}')
    repo_cache_folder = vlm_options.repo_id.replace('/', '--')
    if artifacts_path is None:
        artifacts_path = self.download_models(self.vlm_options.repo_id, revision=self.vlm_options.revision)
    elif (artifacts_path / repo_cache_folder).exists():
        artifacts_path = artifacts_path / repo_cache_folder
    else:
        available_models = []
        if artifacts_path.exists():
            available_models = [p.name for p in artifacts_path.iterdir() if p.is_dir()]
        raise FileNotFoundError(f"Model '{self.vlm_options.repo_id}' not found in artifacts_path.\nExpected location: {artifacts_path / repo_cache_folder}\nAvailable models in {artifacts_path}: {(', '.join(available_models) if available_models else 'none')}\n\nTo fix this issue:\n  1. Download the model: docling-tools models download-hf-repo {self.vlm_options.repo_id}\n  2. Or remove --artifacts-path to enable auto-download\n  3. Or use a different model that exists in your artifacts_path")
    extra_cfg = self.vlm_options.extra_generation_config
    load_cfg = {k: v for (k, v) in extra_cfg.items() if k in self._VLLM_ENGINE_KEYS}
    gen_cfg = {k: v for (k, v) in extra_cfg.items() if k in self._VLLM_SAMPLING_KEYS}
    unknown = sorted((k for k in extra_cfg.keys() if k not in self._VLLM_ENGINE_KEYS and k not in self._VLLM_SAMPLING_KEYS))
    if unknown:
        _log.warning('Ignoring unknown extra_generation_config keys for vLLM: %s', unknown)
    llm_kwargs: Dict[str, Any] = {'model': str(artifacts_path), 'model_impl': 'transformers', 'limit_mm_per_prompt': {'image': 1}, 'revision': self.vlm_options.revision, 'trust_remote_code': self.vlm_options.trust_remote_code, **load_cfg}
    if self.device == 'cpu':
        llm_kwargs.setdefault('enforce_eager', True)
    else:
        llm_kwargs.setdefault('gpu_memory_utilization', 0.3)
    if self.vlm_options.quantized and self.vlm_options.load_in_8bit:
        llm_kwargs.setdefault('quantization', 'bitsandbytes')
    self.llm = LLM(**llm_kwargs)
    self.processor = AutoProcessor.from_pretrained(artifacts_path, trust_remote_code=self.vlm_options.trust_remote_code, revision=self.vlm_options.revision)
    self.sampling_params = SamplingParams(temperature=self.temperature, max_tokens=self.max_new_tokens, stop=self.vlm_options.stop_strings or None, **gen_cfg)