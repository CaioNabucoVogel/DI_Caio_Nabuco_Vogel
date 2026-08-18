class PartialRender:
    """
    Some parts of a template need to be generated at the end, but
    inserted into the template at the start.  This allows doing a bunch
    of replacements after the initial render.
    """
    HookFn = Callable[[], str]

    def __init__(self, code: str, replacement_hooks: dict[str, Optional[HookFn]]) -> None:
        super().__init__()
        self._code: str = code
        self.replacement_hooks: dict[str, Optional[PartialRender.HookFn]] = replacement_hooks

    @property
    def code(self) -> str:
        """
        The fully rendered code. Will **error** if any hooks have yet to be
        finalized.
        """
        remaining_active_hooks = [key for (key, fn) in self.replacement_hooks.items() if fn is not None]
        assert len(remaining_active_hooks) == 0, f'The following hooks have not yet been finalized:\n remaining_active_hooks={remaining_active_hooks!r}'
        return self._code

    def finalize_hook(self, hook_key: str, strict: bool=True) -> None:
        """
        Finalize a hook by name.

        :param strict: If ``True``, raise an error if the hook wasn't found.

        NOTE: Will **error** if the hook has already been finalized.
        """
        if hook_key not in self.replacement_hooks:
            if strict:
                raise RuntimeError(f'{hook_key} not registered in self.replacement_hooks')
            else:
                return
        hook = self.replacement_hooks[hook_key]
        assert hook is not None, f'Hook key {hook_key} can only be called once'
        self._code = self._code.replace(hook_key, hook())
        self.replacement_hooks[hook_key] = None

    def finalize_remaining(self) -> str:
        """
        Finalize the remaining active hooks. This function can be used in cases
        where the caller uses `finalize_hook` rather than `finalize_all`.
        Note: `finalize_all` errors if a hook that has already been finalized
        is attempted to be called again. This function only attempts to
        finalize active hooks.
        """
        for (key, fn) in self.replacement_hooks.items():
            if fn is not None:
                self.finalize_hook(key)
        return self.code

    def finalize_all(self) -> str:
        """
        Finalize all active hooks.

        NOTE: unlike ``finalize_remaining``, this method will **error** if any
        hook has already been finalized.
        """
        for key in self.replacement_hooks:
            self.finalize_hook(key)
        return self.code