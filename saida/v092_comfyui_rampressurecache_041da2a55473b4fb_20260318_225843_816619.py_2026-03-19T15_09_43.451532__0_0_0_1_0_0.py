def _ram_gb():
    return psutil.virtual_memory().available / 1024 ** 3