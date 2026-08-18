def _load_pretrained_model(cls, model: 'PreTrainedModel', state_dict: dict | None, checkpoint_files: list[str] | None, pretrained_model_name_or_path: str | None, ignore_mismatched_sizes: bool=False, sharded_metadata: dict | None=None, device_map: dict | None=None, disk_offload_folder: str | None=None, offload_buffers: bool=False, dtype: torch.dtype | None=None, hf_quantizer: HfQuantizer | None=None, device_mesh: Optional['torch.distributed.device_mesh.DeviceMesh']=None, weights_only: bool=True, weight_mapping: Sequence[WeightConverter | WeightRenaming] | None=None):
    is_quantized = hf_quantizer is not None
    is_hqq_or_quark = is_quantized and hf_quantizer.quantization_config.quant_method in {QuantizationMethod.HQQ, QuantizationMethod.QUARK}
    expected_keys = list(model.state_dict().keys())
    if logger.level >= logging.WARNING:
        verify_tp_plan(expected_keys, getattr(model, '_tp_plan', None))
    disk_offload_index = None
    if device_map is not None and 'disk' in device_map.values():
        disk_offload_index = accelerate_disk_offload(model, disk_offload_folder, checkpoint_files, device_map, sharded_metadata, dtype, weight_mapping)
    if device_map is not None and (not is_hqq_or_quark):
        expanded_device_map = expand_device_map(device_map, expected_keys)
        caching_allocator_warmup(model, expanded_device_map, hf_quantizer)
    error_msgs = []
    if is_deepspeed_zero3_enabled() and (not is_quantized):
        if state_dict is None:
            merged_state_dict = {}
            for ckpt_file in checkpoint_files:
                merged_state_dict.update(load_state_dict(ckpt_file, map_location='cpu', weights_only=weights_only))
            state_dict = merged_state_dict
        (error_msgs, missing_keys) = _load_state_dict_into_zero3_model(model, state_dict)
        (unexpected_keys, mismatched_keys, conversion_errors) = (set(), set(), set())
    else:
        all_pointer = set()
        if checkpoint_files is not None and checkpoint_files[0].endswith('.safetensors'):
            merged_state_dict = {}
            for file in checkpoint_files:
                file_pointer = safe_open(file, framework='pt', device='cpu')
                all_pointer.add(file_pointer)
                for k in file_pointer.keys():
                    merged_state_dict[k] = file_pointer.get_slice(k)
        elif state_dict is not None:
            merged_state_dict = state_dict
        elif checkpoint_files is not None:
            merged_state_dict = {}
            for ckpt_file in checkpoint_files:
                merged_state_dict.update(load_state_dict(ckpt_file))
        else:
            raise ValueError('Neither a state dict nor checkpoint files were found.')
        (missing_keys, unexpected_keys, mismatched_keys, disk_offload_index, conversion_errors) = convert_and_load_state_dict_in_model(model=model, state_dict=merged_state_dict, weight_mapping=weight_mapping, tp_plan=model._tp_plan, hf_quantizer=hf_quantizer, dtype=dtype, device_map=device_map, dtype_plan=model.dtype_plan, device_mesh=device_mesh, disk_offload_index=disk_offload_index, disk_offload_folder=disk_offload_folder, offload_buffers=offload_buffers)
        for k in all_pointer:
            k.__exit__(None, None, None)
    model.mark_tied_weights_as_initialized()
    missing_and_mismatched = missing_keys | {k[0] for k in mismatched_keys}
    model._move_missing_keys_from_meta_to_device(missing_and_mismatched, device_map, device_mesh, hf_quantizer)
    model._initialize_missing_keys(is_quantized)
    model.tie_weights(missing_keys=missing_keys, recompute_mapping=False)
    (missing_keys, unexpected_keys) = model._adjust_missing_and_unexpected_keys(missing_keys, unexpected_keys)
    log_state_dict_report(model=model, pretrained_model_name_or_path=pretrained_model_name_or_path, logger=logger, error_msgs=error_msgs, unexpected_keys=unexpected_keys, missing_keys=missing_keys, mismatched_keys=mismatched_keys, mismatched_shapes=mismatched_keys, conversion_errors=conversion_errors, ignore_mismatched_sizes=ignore_mismatched_sizes)
    return (model, missing_keys, unexpected_keys, mismatched_keys, disk_offload_index, error_msgs)