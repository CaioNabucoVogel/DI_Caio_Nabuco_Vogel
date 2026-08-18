def poll(self, ram_headroom):

    def _ram_gb():
        return psutil.virtual_memory().available / 1024 ** 3
    if _ram_gb() > ram_headroom:
        return
    gc.collect()
    if _ram_gb() > ram_headroom:
        return
    clean_list = []
    for (key, (outputs, _)) in self.cache.items():
        oom_score = RAM_CACHE_OLD_WORKFLOW_OOM_MULTIPLIER ** (self.generation - self.used_generation[key])
        ram_usage = RAM_CACHE_DEFAULT_RAM_USAGE

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
        scan_list_for_ram_usage(outputs)
        oom_score *= ram_usage
        bisect.insort(clean_list, (oom_score, self.timestamps[key], key))
    while _ram_gb() < ram_headroom * RAM_CACHE_HYSTERESIS and clean_list:
        (_, _, key) = clean_list.pop()
        del self.cache[key]
        gc.collect()