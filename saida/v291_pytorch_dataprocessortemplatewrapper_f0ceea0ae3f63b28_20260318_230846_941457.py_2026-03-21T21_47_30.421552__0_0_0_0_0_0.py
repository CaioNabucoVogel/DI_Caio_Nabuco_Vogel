class DataProcessorTemplateWrapper:
    """
    A wrapper class for a kernel template.

    This class together with `DataProcessorChoiceCallerWrapper` provides a convenient way to
    preprocess and postprocess data before and after using the wrapped template. A typical
    usage is to reorder or filter the input nodes in order to match the expected input of other
    kernel choices like a ATen kernel. A more complicated usage is to prepack the weights.
    See the example from :mod:`cpp_gemm_template` for more details.
    """

    def __init__(self, wrapped_template_cls, preprocessor, postprocessor, **kwargs) -> None:
        if preprocessor is not None:
            self._preprocessor = preprocessor
        else:
            self._preprocessor = lambda x, y: (x, y)
        if postprocessor is not None:
            self._postprocessor = postprocessor
        else:
            self._postprocessor = lambda x: x
        assert 'input_nodes' in kwargs
        assert 'layout' in kwargs
        (kwargs['input_nodes'], kwargs['layout']) = preprocessor(kwargs['input_nodes'], kwargs['layout'])
        self._wrapped = wrapped_template_cls(**kwargs)

    def __getattr__(self, name):
        return getattr(self._wrapped, name)

    def maybe_append_choice(self, choices, **kwargs):
        return type(self._wrapped).maybe_append_choice(self, choices, **kwargs)

    def generate(self, **kwargs):
        choice_caller = self._wrapped.generate(**kwargs)
        return DataProcessorChoiceCallerWrapper(choice_caller, self._preprocessor, self._postprocessor)

    def __repr__(self) -> str:
        return f'DataProcessorTemplateWrapper({self._wrapped})'