def __init__(self, embed_dim, num_heads, bias=True, dtype=None, device=None, operations=None):
    super().__init__()
    self.embed_dim = embed_dim
    self.num_heads = num_heads
    self.head_dim = embed_dim // num_heads
    self.k_proj = operations.Linear(embed_dim, embed_dim, bias=bias, device=device, dtype=dtype)
    self.v_proj = operations.Linear(embed_dim, embed_dim, bias=bias, device=device, dtype=dtype)
    self.q_proj = operations.Linear(embed_dim, embed_dim, bias=bias, device=device, dtype=dtype)
    self.out_proj = operations.Linear(embed_dim, embed_dim, bias=bias, device=device, dtype=dtype)