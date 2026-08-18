def scan_list_for_ram_usage(outputs):
    nonlocal ram_usage
    if outputs is None:
        return
    for output in outputs:
        if isinstance(output, list):
            scan_list_for_ram_usage(output)
        elif isinstance(output, torch.Tensor) and output.device.type == 'cpu':
            ram_usage += output.numel() * output.element_size() * 0.5
        elif hasattr(output, 'get_ram_usage'):
            ram_usage += output.get_ram_usage()