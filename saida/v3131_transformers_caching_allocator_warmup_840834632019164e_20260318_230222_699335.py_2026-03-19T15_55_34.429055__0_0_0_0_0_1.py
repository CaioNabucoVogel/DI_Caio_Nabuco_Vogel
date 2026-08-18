def caching_allocator_warmup(model: PreTrainedModel, expanded_device_map: dict, hf_quantizer: HfQuantizer | None):
    """This function warm-ups the caching allocator based on the size of the model tensors that will reside on each
    device. It allows to have one large call to Malloc, instead of recursively calling it later when loading
    the model, which is actually the loading speed bottleneck.
    Calling this function allows to cut the model loading time by a very large margin.

    A few facts related to loading speed (taking into account the use of this function):
    - When loading a model the first time, it is usually slower than the subsequent times, because the OS is very likely
    to cache the different state dicts (if enough resources/RAM are available)
    - Trying to force the OS to cache the files in advance (by e.g. accessing a small portion of them) is really hard,
    and not a good idea in general as this is low level OS optimizations that depend on resource usage anyway
    - As of 18/03/2025, loading a Llama 70B model with TP takes ~1 min without file cache, and ~13s with full file cache.
    The baseline, i.e. only loading the tensor shards on device and adjusting dtype (i.e. copying them) is ~5s with full cache.
    These numbers are reported for TP on 4 H100 GPUs.
    - It is useless to pre-allocate more than the model size in this function (i.e. using an `allocation_factor` > 1) as
    cudaMalloc is not a bottleneck at all anymore
    - Loading speed bottleneck is now almost only tensor copy (i.e. changing the dtype) and moving the tensors to the devices.
    However, we cannot really improve on those aspects obviously, as the data needs to be moved/copied in the end.
    """
    accelerator_device_map = {param: torch.device(device) for (param, device) in expanded_device_map.items() if is_accelerator_device(device)}
    if not accelerator_device_map:
        return
    total_byte_count = get_total_byte_count(model, accelerator_device_map, hf_quantizer)
    for (device, byte_count) in total_byte_count.items():
        if device.type in ['cuda', 'xpu']:
            torch_accelerator_module = getattr(torch, device.type)
            index = device.index if device.index is not None else torch_accelerator_module.current_device()
            device_memory = torch_accelerator_module.mem_get_info(index)[0]
            byte_count = min(byte_count, max(0, int(device_memory - 1.2 * 1024 ** 3)))
            unused_memory = torch_accelerator_module.memory_reserved(index) - torch_accelerator_module.memory_allocated(index)
            byte_count = int(max(0, byte_count - unused_memory))
        _ = torch.empty(byte_count // 2, dtype=torch.float16, device=device, requires_grad=False)