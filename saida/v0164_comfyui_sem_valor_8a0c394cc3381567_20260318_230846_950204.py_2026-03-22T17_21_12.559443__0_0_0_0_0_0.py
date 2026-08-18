def __init__(self, embed_dim, heads, layer_norm_eps, dtype, device, operations):
    super().__init__()
    self.attention = BertAttention(embed_dim, heads, dtype, device, operations)
    self.output = Dino2AttentionOutput(embed_dim, embed_dim, layer_norm_eps, dtype, device, operations)