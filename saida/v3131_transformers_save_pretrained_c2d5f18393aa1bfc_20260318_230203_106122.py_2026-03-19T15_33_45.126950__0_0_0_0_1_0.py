def save_pretrained(self, save_directory: str | os.PathLike, is_main_process: bool=True, state_dict: dict | None=None, push_to_hub: bool=False, max_shard_size: int | str='50GB', variant: str | None=None, token: str | bool | None=None, save_peft_format: bool=True, save_original_format: bool=True, **kwargs):
    """
        Save a model and its configuration file to a directory, so that it can be re-loaded using the
        [`~PreTrainedModel.from_pretrained`] class method.

        Arguments:
            save_directory (`str` or `os.PathLike`):
                Directory to which to save. Will be created if it doesn't exist.
            is_main_process (`bool`, *optional*, defaults to `True`):
                Whether the process calling this is the main process or not. Useful when in distributed training like
                TPUs and need to call this function on all processes. In this case, set `is_main_process=True` only on
                the main process to avoid race conditions.
            state_dict (nested dictionary of `torch.Tensor`):
                The state dictionary of the model to save. Will default to `self.state_dict()`, but can be used to only
                save parts of the model or if special precautions need to be taken when recovering the state dictionary
                of a model (like when using model parallelism).
            push_to_hub (`bool`, *optional*, defaults to `False`):
                Whether or not to push your model to the Hugging Face model hub after saving it. You can specify the
                repository you want to push to with `repo_id` (will default to the name of `save_directory` in your
                namespace).
            max_shard_size (`int` or `str`, *optional*, defaults to `"50GB"`):
                The maximum size for a checkpoint before being sharded. Checkpoints shard will then be each of size
                lower than this size. If expressed as a string, needs to be digits followed by a unit (like `"5MB"`).

                <Tip warning={true}>

                If a single weight of the model is bigger than `max_shard_size`, it will be in its own checkpoint shard
                which will be bigger than `max_shard_size`.

                </Tip>

            variant (`str`, *optional*):
                If specified, weights are saved in the format model.<variant>.safetensors.
            token (`str` or `bool`, *optional*):
                The token to use as HTTP bearer authorization for remote files. If `True`, or not specified, will use
                the token generated when running `hf auth login` (stored in `~/.huggingface`).
            save_peft_format (`bool`, *optional*, defaults to `True`):
                For backward compatibility with PEFT library, in case adapter weights are attached to the model, all
                keys of the state dict of adapters needs to be prepended with `base_model.model`. Advanced users can
                disable this behaviours by setting `save_peft_format` to `False`.
            save_original_format (`bool`, *optional*, defaults to `True`):
                For backward compatibility with the previous versions of `transfomers` you can save the checkpoint with
                its reverse mapping. The reverse mapping needs to exists even if the model was loaded from a None legacy
                checkpoint.
            kwargs (`dict[str, Any]`, *optional*):
                Additional key word arguments passed along to the [`~utils.PushToHubMixin.push_to_hub`] method.
        """
    if token is not None:
        kwargs['token'] = token
    _hf_peft_config_loaded = getattr(self, '_hf_peft_config_loaded', False)
    hf_quantizer = getattr(self, 'hf_quantizer', None)
    quantization_serializable = hf_quantizer is not None and isinstance(hf_quantizer, HfQuantizer) and hf_quantizer.is_serializable()
    if hf_quantizer is not None and (not _hf_peft_config_loaded) and (not quantization_serializable):
        raise ValueError(f'The model is quantized with {hf_quantizer.quantization_config.quant_method} and is not serializable - check out the warnings from the logger on the traceback to understand the reason why the quantized model is not serializable.')
    if self._tp_size is not None and (not is_huggingface_hub_greater_or_equal('0.31.4')):
        raise ImportError('Saving a model with tensor parallelism requires `huggingface_hub` version 0.31.4 or higher.')
    if os.path.isfile(save_directory):
        logger.error(f'Provided path ({save_directory}) should be a directory, not a file')
        return
    os.makedirs(save_directory, exist_ok=True)
    if push_to_hub:
        commit_message = kwargs.pop('commit_message', None)
        repo_id = kwargs.pop('repo_id', save_directory.split(os.path.sep)[-1])
        create_pr = kwargs.pop('create_pr', False)
        repo_id = create_repo(repo_id, exist_ok=True, **kwargs).repo_id
        files_timestamps = self._get_files_timestamps(save_directory)
    metadata = {}
    if hf_quantizer is not None:
        (state_dict, metadata) = hf_quantizer.get_state_dict_and_metadata(self)
    metadata['format'] = 'pt'
    model_to_save = unwrap_model(self)
    dtype = model_to_save.dtype
    model_to_save.config.dtype = str(dtype).split('.')[1]
    model_to_save.config.architectures = [model_to_save.__class__.__name__.removeprefix('FSDP')]
    if self._auto_class is not None:
        custom_object_save(self, save_directory, config=self.config)
    if is_main_process:
        if not _hf_peft_config_loaded:
            model_to_save.config.save_pretrained(save_directory)
        if self.can_generate():
            model_to_save.generation_config.save_pretrained(save_directory)
        if _hf_peft_config_loaded:
            logger.info('Detected adapters on the model, saving the model in the PEFT format, only adapter weights will be saved.')
            state_dict = model_to_save.get_adapter_state_dict(state_dict=state_dict)
            if save_peft_format:
                logger.info('To match the expected format of the PEFT library, all keys of the state dict of adapters will be prepended with `base_model.model`.')
                peft_state_dict = {}
                for (key, value) in state_dict.items():
                    peft_state_dict[f'base_model.model.{key}'] = value
                state_dict = peft_state_dict
            active_adapter = self.active_adapters()
            if len(active_adapter) > 1:
                raise ValueError('Multiple active adapters detected, saving multiple active adapters is not supported yet. You can save adapters separately one by one by iteratively calling `model.set_adapter(adapter_name)` then `model.save_pretrained(...)`')
            active_adapter = active_adapter[0]
            current_peft_config = self.peft_config[active_adapter]
            current_peft_config.save_pretrained(save_directory)
    if state_dict is None:
        state_dict = model_to_save.state_dict()
    is_offloaded = False
    if hasattr(self, 'hf_device_map') and len(set(self.hf_device_map.values())) > 1 and ('cpu' in self.hf_device_map.values() or 'disk' in self.hf_device_map.values()):
        is_offloaded = True
        warnings.warn('Attempting to save a model with offloaded modules. Ensure that unallocated cpu memory exceeds the `shard_size` (50GB default)')
    if IS_SAGEMAKER_MP_POST_1_10:
        for (smp_to_hf, _) in smp.state.module_manager.translate_functions:
            state_dict = smp_to_hf(state_dict)
    if self._keys_to_ignore_on_save is not None:
        for ignore_key in self._keys_to_ignore_on_save:
            if ignore_key in state_dict:
                del state_dict[ignore_key]
    if self._tp_size is not None:
        state_dict = replace_state_dict_local_with_dtensor(state_dict, self._tp_plan, self._device_mesh)
    state_dict = remove_tied_weights_from_state_dict(state_dict, model_to_save)
    if save_original_format:
        state_dict = revert_weight_conversion(model_to_save, state_dict)
    if not _hf_peft_config_loaded:
        weights_name = SAFE_WEIGHTS_NAME
        weights_name = _add_variant(weights_name, variant)
    else:
        weights_name = ADAPTER_SAFE_WEIGHTS_NAME
    filename_pattern = weights_name.replace('.bin', '{suffix}.bin').replace('.safetensors', '{suffix}.safetensors')
    state_dict_split = split_torch_state_dict_into_shards(state_dict, filename_pattern=filename_pattern, max_shard_size=max_shard_size)
    index = None
    if state_dict_split.is_sharded:
        index = {'metadata': {'total_parameters': self.num_parameters(), **state_dict_split.metadata}, 'weight_map': state_dict_split.tensor_to_filename}
    for filename in os.listdir(save_directory):
        full_filename = os.path.join(save_directory, filename)
        weights_no_suffix = weights_name.replace('.bin', '').replace('.safetensors', '')
        filename_no_suffix = filename.replace('.bin', '').replace('.safetensors', '')
        reg = re.compile('(.*?)-\\d{5}-of-\\d{5}')
        if filename.startswith(weights_no_suffix) and os.path.isfile(full_filename) and (filename not in state_dict_split.filename_to_tensors) and is_main_process and (reg.fullmatch(filename_no_suffix) is not None):
            os.remove(full_filename)
    for (shard_file, tensor_names) in logging.tqdm(state_dict_split.filename_to_tensors.items(), desc='Writing model shards'):
        filename = os.path.join(save_directory, shard_file)
        shard_state_dict = {}
        for tensor_name in tensor_names:
            tensor = state_dict.pop(tensor_name)
            if _is_dtensor_available and isinstance(tensor, DTensor):
                tensor = tensor.full_tensor()
                if _get_parameter_tp_plan(tensor_name, self._tp_plan) == 'local_packed_rowwise':
                    tensor = repack_weights(tensor, -1, self._tp_size, 2)
            if is_offloaded and tensor.device.type == 'meta':
                tensor = load_offloaded_parameter(model_to_save, tensor_name)
            shard_state_dict[tensor_name] = tensor.contiguous()
        safe_save_file(shard_state_dict, filename, metadata=metadata)
        del shard_state_dict
    if index is None:
        path_to_weights = os.path.join(save_directory, weights_name)
        logger.info(f'Model weights saved in {path_to_weights}')
    else:
        save_index_file = SAFE_WEIGHTS_INDEX_NAME
        save_index_file = os.path.join(save_directory, _add_variant(save_index_file, variant))
        with open(save_index_file, 'w', encoding='utf-8') as f:
            content = json.dumps(index, indent=2, sort_keys=True) + '\n'
            f.write(content)
        logger.info(f'The model is bigger than the maximum size per checkpoint ({max_shard_size}) and is going to be split in {len(state_dict_split.filename_to_tensors)} checkpoint shards. You can find where each parameters has been saved in the index located at {save_index_file}.')
    if push_to_hub:
        model_card = create_and_tag_model_card(repo_id, self.model_tags, token=token)
        model_card.save(os.path.join(save_directory, 'README.md'))
        self._upload_modified_files(save_directory, repo_id, files_timestamps, commit_message=commit_message, token=token, create_pr=create_pr)