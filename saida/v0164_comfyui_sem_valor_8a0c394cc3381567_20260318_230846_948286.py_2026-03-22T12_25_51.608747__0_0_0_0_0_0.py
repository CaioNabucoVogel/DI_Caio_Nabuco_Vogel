def __init__(self, config: Llama2Config, device=None, dtype=None, ops: Any=None):
    super().__init__()
    self.num_heads = config.num_attention_heads
    self.num_kv_heads = config.num_key_value_heads
    self.hidden_size = config.hidden_size
    self.head_dim = config.head_dim
    self.inner_size = self.num_heads * self.head_dim
    ops = ops or nn
    self.q_proj = ops.Linear(config.hidden_size, self.inner_size, bias=config.qkv_bias, device=device, dtype=dtype)
    self.k_proj = ops.Linear(config.hidden_size, self.num_kv_heads * self.head_dim, bias=config.qkv_bias, device=device, dtype=dtype)
    self.v_proj = ops.Linear(config.hidden_size, self.num_kv_heads * self.head_dim, bias=config.qkv_bias, device=device, dtype=dtype)
    self.o_proj = ops.Linear(self.inner_size, config.hidden_size, bias=False, device=device, dtype=dtype)
    self.q_norm = None
    self.k_norm = None
    if config.q_norm == 'gemma3':
        self.q_norm = RMSNorm(self.head_dim, eps=config.rms_norm_eps, add=config.rms_norm_add, device=device, dtype=dtype)
    if config.k_norm == 'gemma3':
        self.k_norm = RMSNorm(self.head_dim, eps=config.rms_norm_eps, add=config.rms_norm_add, device=device, dtype=dtype)