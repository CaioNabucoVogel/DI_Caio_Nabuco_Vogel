def __init__(self) -> None:
    super().__init__(autowrap_modules=())
    self.tensor_tracker = WeakTensorKeyDictionary()
    self.symnode_tracker = _SymNodeDict()
    self.script_object_tracker = WeakIdKeyDictionary(dict=None, ref_type=_WeakHashRef)
    self.sympy_expr_tracker = {}
    self.torch_fn_metadata = None
    self.torch_fn_counts = {}
    self.enable_thunkify = False