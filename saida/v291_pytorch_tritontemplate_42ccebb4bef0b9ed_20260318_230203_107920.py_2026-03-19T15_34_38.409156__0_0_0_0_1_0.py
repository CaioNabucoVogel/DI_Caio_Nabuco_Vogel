def maybe_append_choice(self, choices: list[Any], **kwargs: Any) -> Optional[NotImplementedError]:
    """
        Maybe generates a new ChoiceCaller and appends it into existing choices.
        Returns None if success, otherwise returns the error.

        choices: A list of ChoiceCallers.
        kwargs: Additional kwargs to be passed to self.generate() to generate a new ChoiceCaller.
        """
    try:
        choice = self.generate(generate_with_caching=True, **kwargs)
        if choice is not None:
            choices.append(choice)
        return None
    except NotImplementedError as e:
        log.info('Cannot Append Choice: %s. KernelTemplate type is %s', e, type(self), stack_info=log.getEffectiveLevel() < logging.INFO)
        return e