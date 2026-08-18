def __init__(self, scale: Tensor | float, concentration: Tensor | float, validate_args: bool | None=None) -> None:
    (self.scale, self.concentration) = broadcast_all(scale, concentration)
    self.concentration_reciprocal = self.concentration.reciprocal()
    base_dist = Exponential(torch.ones_like(self.scale), validate_args=validate_args)
    transforms = [PowerTransform(exponent=self.concentration_reciprocal), AffineTransform(loc=0, scale=self.scale)]
    super().__init__(base_dist, transforms, validate_args=validate_args)