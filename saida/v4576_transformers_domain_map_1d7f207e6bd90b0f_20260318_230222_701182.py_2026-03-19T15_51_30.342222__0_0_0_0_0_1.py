def domain_map(cls, df: torch.Tensor, loc: torch.Tensor, scale: torch.Tensor):
    scale = cls.squareplus(scale).clamp_min(torch.finfo(scale.dtype).eps)
    df = 2.0 + cls.squareplus(df)
    return (df.squeeze(-1), loc.squeeze(-1), scale.squeeze(-1))