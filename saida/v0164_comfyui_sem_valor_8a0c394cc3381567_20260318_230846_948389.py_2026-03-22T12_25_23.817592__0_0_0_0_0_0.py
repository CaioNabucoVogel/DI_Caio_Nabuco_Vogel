def forward(self, query: torch.Tensor, key: torch.Tensor, value: torch.Tensor, mask: Optional[torch.Tensor]=None) -> torch.Tensor:
    (batch_size, seq_len, _) = query.shape
    q = self.q_proj(query)
    k = self.k_proj(key)
    v = self.v_proj(value)
    attn_output = optimized_attention_masked(q, k, v, self.n_heads, mask)
    attn_output = self.out_proj(attn_output)
    return attn_output