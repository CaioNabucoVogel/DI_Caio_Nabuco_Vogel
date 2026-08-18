def auto_wrapper_callable(m, *args, **kwargs):
    target_cls = FSDP if not self.is_fsdp_xla_v2_enabled else FSDPv2
    return target_cls(checkpoint_module(m), *args, **kwargs)