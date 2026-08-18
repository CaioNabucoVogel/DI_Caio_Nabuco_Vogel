def __init__(self, max_img_h: int, max_img_w: int, max_frames: int, in_channels: int, out_channels: int, patch_spatial: int, patch_temporal: int, concat_padding_mask: bool=True, model_channels: int=768, num_blocks: int=10, num_heads: int=16, mlp_ratio: float=4.0, crossattn_emb_channels: int=1024, pos_emb_cls: str='sincos', pos_emb_learnable: bool=False, pos_emb_interpolation: str='crop', min_fps: int=1, max_fps: int=30, use_adaln_lora: bool=False, adaln_lora_dim: int=256, rope_h_extrapolation_ratio: float=1.0, rope_w_extrapolation_ratio: float=1.0, rope_t_extrapolation_ratio: float=1.0, extra_per_block_abs_pos_emb: bool=False, extra_h_extrapolation_ratio: float=1.0, extra_w_extrapolation_ratio: float=1.0, extra_t_extrapolation_ratio: float=1.0, rope_enable_fps_modulation: bool=True, image_model=None, device=None, dtype=None, operations=None) -> None:
    super().__init__()
    self.dtype = dtype
    self.max_img_h = max_img_h
    self.max_img_w = max_img_w
    self.max_frames = max_frames
    self.in_channels = in_channels
    self.out_channels = out_channels
    self.patch_spatial = patch_spatial
    self.patch_temporal = patch_temporal
    self.num_heads = num_heads
    self.num_blocks = num_blocks
    self.model_channels = model_channels
    self.concat_padding_mask = concat_padding_mask
    self.pos_emb_cls = pos_emb_cls
    self.pos_emb_learnable = pos_emb_learnable
    self.pos_emb_interpolation = pos_emb_interpolation
    self.min_fps = min_fps
    self.max_fps = max_fps
    self.rope_h_extrapolation_ratio = rope_h_extrapolation_ratio
    self.rope_w_extrapolation_ratio = rope_w_extrapolation_ratio
    self.rope_t_extrapolation_ratio = rope_t_extrapolation_ratio
    self.extra_per_block_abs_pos_emb = extra_per_block_abs_pos_emb
    self.extra_h_extrapolation_ratio = extra_h_extrapolation_ratio
    self.extra_w_extrapolation_ratio = extra_w_extrapolation_ratio
    self.extra_t_extrapolation_ratio = extra_t_extrapolation_ratio
    self.rope_enable_fps_modulation = rope_enable_fps_modulation
    self.build_pos_embed(device=device, dtype=dtype)
    self.use_adaln_lora = use_adaln_lora
    self.adaln_lora_dim = adaln_lora_dim
    self.t_embedder = nn.Sequential(Timesteps(model_channels), TimestepEmbedding(model_channels, model_channels, use_adaln_lora=use_adaln_lora, device=device, dtype=dtype, operations=operations))
    in_channels = in_channels + 1 if concat_padding_mask else in_channels
    self.x_embedder = PatchEmbed(spatial_patch_size=patch_spatial, temporal_patch_size=patch_temporal, in_channels=in_channels, out_channels=model_channels, device=device, dtype=dtype, operations=operations)
    self.blocks = nn.ModuleList([Block(x_dim=model_channels, context_dim=crossattn_emb_channels, num_heads=num_heads, mlp_ratio=mlp_ratio, use_adaln_lora=use_adaln_lora, adaln_lora_dim=adaln_lora_dim, device=device, dtype=dtype, operations=operations) for _ in range(num_blocks)])
    self.final_layer = FinalLayer(hidden_size=self.model_channels, spatial_patch_size=self.patch_spatial, temporal_patch_size=self.patch_temporal, out_channels=self.out_channels, use_adaln_lora=self.use_adaln_lora, adaln_lora_dim=self.adaln_lora_dim, device=device, dtype=dtype, operations=operations)
    self.t_embedding_norm = operations.RMSNorm(model_channels, eps=1e-06, device=device, dtype=dtype)