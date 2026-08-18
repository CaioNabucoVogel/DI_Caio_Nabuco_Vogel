def __init__(self, kernel, subgraph_number: int, fixed_inputs: dict[str, Any], mask: Optional[str]):
    super().__init__(V.ops)
    self.name = f'PlaceholderSubstitution_{subgraph_number}'
    self.kernel = kernel
    self.fixed_inputs = fixed_inputs
    self.mask = mask