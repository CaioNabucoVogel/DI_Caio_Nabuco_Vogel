def generate_code(kernel) -> Optional[tuple[str, str]]:

    def make_extra() -> str:
        extra_parts = [f'{kwarg}={repr(kwargs[kwarg])}' for kwarg in sorted(kwargs.keys())]
        extra_parts.extend([f'num_stages={num_stages}', f'num_warps={num_warps}'])
        if HAS_WARP_SPEC:
            extra_parts.extend([f'num_consumer_groups={num_consumer_groups}', f'num_buffers_warp_spec={num_buffers_warp_spec}'])
        extra = '-'.join(extra_parts) + '-'
        return extra
    try:
        template = kernel.render(self.template, kwargs, caching_enabled)
        code = template.finalize_all()
    except ZeroDivisionError:
        return None
    if self.debug:
        print('Generated Code:\n', code)
    extra = make_extra()
    return (code, extra)