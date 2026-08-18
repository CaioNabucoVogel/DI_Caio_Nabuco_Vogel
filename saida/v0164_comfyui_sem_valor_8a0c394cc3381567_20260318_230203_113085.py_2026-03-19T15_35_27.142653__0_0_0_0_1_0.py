def build_pos_embed(self, device=None, dtype=None) -> None:
    if self.pos_emb_cls == 'rope3d':
        cls_type = VideoRopePosition3DEmb
    else:
        raise ValueError(f'Unknown pos_emb_cls {self.pos_emb_cls}')
    logging.debug(f'Building positional embedding with {self.pos_emb_cls} class, impl {cls_type}')
    kwargs = dict(model_channels=self.model_channels, len_h=self.max_img_h // self.patch_spatial, len_w=self.max_img_w // self.patch_spatial, len_t=self.max_frames // self.patch_temporal, max_fps=self.max_fps, min_fps=self.min_fps, is_learnable=self.pos_emb_learnable, interpolation=self.pos_emb_interpolation, head_dim=self.model_channels // self.num_heads, h_extrapolation_ratio=self.rope_h_extrapolation_ratio, w_extrapolation_ratio=self.rope_w_extrapolation_ratio, t_extrapolation_ratio=self.rope_t_extrapolation_ratio, enable_fps_modulation=self.rope_enable_fps_modulation, device=device)
    self.pos_embedder = cls_type(**kwargs)
    if self.extra_per_block_abs_pos_emb:
        kwargs['h_extrapolation_ratio'] = self.extra_h_extrapolation_ratio
        kwargs['w_extrapolation_ratio'] = self.extra_w_extrapolation_ratio
        kwargs['t_extrapolation_ratio'] = self.extra_t_extrapolation_ratio
        kwargs['device'] = device
        kwargs['dtype'] = dtype
        self.extra_pos_embedder = LearnablePosEmbAxis(**kwargs)