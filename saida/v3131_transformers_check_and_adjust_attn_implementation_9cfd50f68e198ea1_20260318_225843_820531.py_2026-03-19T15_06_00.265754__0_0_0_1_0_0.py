def _check_and_adjust_attn_implementation(self, attn_implementation: str | None, is_init_check: bool=False) -> str:
    """
        Check that the `attn_implementation` exists and is supported by the models, and try to get the kernel from hub if
        it matches hf kernels pattern.

        Args:
            attn_implementation (`str` or `None`):
                The attention implementation to check for existence/validity.
            is_init_check (`bool`, *optional*):
                Whether this check is performed early, i.e. at __init__ time, or later when the model and its weights are
                fully instantiated. This is needed as we also check the devices of the weights, which are only available
                later after __init__. This allows to raise proper exceptions early before instantiating the full models
                if we know that the model does not support the requested attention.

        Returns:
            `str`: The final attention implementation to use, including potential fallbacks from sdpa to eager, or from
            None to sdpa (to potentially eager).
        """
    applicable_attn_implementation = attn_implementation
    is_paged = attn_implementation is not None and attn_implementation.startswith('paged|')
    requested_original_flash_attn = attn_implementation is not None and (attn_implementation.removeprefix('paged|') == 'flash_attention_2' or attn_implementation.removeprefix('paged|') == 'flash_attention_3')
    if requested_original_flash_attn and self._supports_flash_attn and (not (is_flash_attn_2_available() or is_flash_attn_3_available())) and is_kernels_available() and (not is_torch_npu_available()):
        applicable_attn_implementation = FLASH_ATTN_KERNEL_FALLBACK[attn_implementation.removeprefix('paged|')]
        if is_torch_xpu_available() and attn_implementation.removeprefix('paged|') == 'flash_attention_2':
            requested_original_flash_attn = False
        if is_paged:
            applicable_attn_implementation = f'paged|{applicable_attn_implementation}'
    if is_kernel(applicable_attn_implementation):
        try:
            if is_paged:
                lazy_import_paged_flash_attention(applicable_attn_implementation)
            else:
                lazy_import_flash_attention(applicable_attn_implementation)
            if requested_original_flash_attn:
                logger.warning_once(f'You do not have `flash_attn` installed, using `{applicable_attn_implementation}` from the `kernels` library instead!')
        except Exception as e:
            if requested_original_flash_attn:
                if attn_implementation.endswith('2'):
                    self._flash_attn_2_can_dispatch()
                else:
                    self._flash_attn_3_can_dispatch()
            raise e
    else:
        applicable_attn_implementation = self.get_correct_attn_implementation(applicable_attn_implementation, is_init_check)
        if is_flash_attention_requested(requested_attention_implementation=applicable_attn_implementation):
            lazy_import_flash_attention(applicable_attn_implementation)
    return applicable_attn_implementation