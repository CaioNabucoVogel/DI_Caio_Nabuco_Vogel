class MiniTrainDIT(nn.Module):
    """
    A clean impl of DIT that can load and  reproduce the training results of the original DIT model in~(cosmos 1)
    A general implementation of adaln-modulated VIT-like~(DiT) transformer for video processing.

    Args:
        max_img_h (int): Maximum height of the input images.
        max_img_w (int): Maximum width of the input images.
        max_frames (int): Maximum number of frames in the video sequence.
        in_channels (int): Number of input channels (e.g., RGB channels for color images).
        out_channels (int): Number of output channels.
        patch_spatial (tuple): Spatial resolution of patches for input processing.
        patch_temporal (int): Temporal resolution of patches for input processing.
        concat_padding_mask (bool): If True, includes a mask channel in the input to handle padding.
        model_channels (int): Base number of channels used throughout the model.
        num_blocks (int): Number of transformer blocks.
        num_heads (int): Number of heads in the multi-head attention layers.
        mlp_ratio (float): Expansion ratio for MLP blocks.
        crossattn_emb_channels (int): Number of embedding channels for cross-attention.
        pos_emb_cls (str): Type of positional embeddings.
        pos_emb_learnable (bool): Whether positional embeddings are learnable.
        pos_emb_interpolation (str): Method for interpolating positional embeddings.
        min_fps (int): Minimum frames per second.
        max_fps (int): Maximum frames per second.
        use_adaln_lora (bool): Whether to use AdaLN-LoRA.
        adaln_lora_dim (int): Dimension for AdaLN-LoRA.
        rope_h_extrapolation_ratio (float): Height extrapolation ratio for RoPE.
        rope_w_extrapolation_ratio (float): Width extrapolation ratio for RoPE.
        rope_t_extrapolation_ratio (float): Temporal extrapolation ratio for RoPE.
        extra_per_block_abs_pos_emb (bool): Whether to use extra per-block absolute positional embeddings.
        extra_h_extrapolation_ratio (float): Height extrapolation ratio for extra embeddings.
        extra_w_extrapolation_ratio (float): Width extrapolation ratio for extra embeddings.
        extra_t_extrapolation_ratio (float): Temporal extrapolation ratio for extra embeddings.
    """

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

    def prepare_embedded_sequence(self, x_B_C_T_H_W: torch.Tensor, fps: Optional[torch.Tensor]=None, padding_mask: Optional[torch.Tensor]=None) -> Tuple[torch.Tensor, Optional[torch.Tensor], Optional[torch.Tensor]]:
        """
        Prepares an embedded sequence tensor by applying positional embeddings and handling padding masks.

        Args:
            x_B_C_T_H_W (torch.Tensor): video
            fps (Optional[torch.Tensor]): Frames per second tensor to be used for positional embedding when required.
                                    If None, a default value (`self.base_fps`) will be used.
            padding_mask (Optional[torch.Tensor]): current it is not used

        Returns:
            Tuple[torch.Tensor, Optional[torch.Tensor]]:
                - A tensor of shape (B, T, H, W, D) with the embedded sequence.
                - An optional positional embedding tensor, returned only if the positional embedding class
                (`self.pos_emb_cls`) includes 'rope'. Otherwise, None.

        Notes:
            - If `self.concat_padding_mask` is True, a padding mask channel is concatenated to the input tensor.
            - The method of applying positional embeddings depends on the value of `self.pos_emb_cls`.
            - If 'rope' is in `self.pos_emb_cls` (case insensitive), the positional embeddings are generated using
                the `self.pos_embedder` with the shape [T, H, W].
            - If "fps_aware" is in `self.pos_emb_cls`, the positional embeddings are generated using the
            `self.pos_embedder` with the fps tensor.
            - Otherwise, the positional embeddings are generated without considering fps.
        """
        if self.concat_padding_mask:
            if padding_mask is None:
                padding_mask = torch.zeros(x_B_C_T_H_W.shape[0], 1, x_B_C_T_H_W.shape[3], x_B_C_T_H_W.shape[4], dtype=x_B_C_T_H_W.dtype, device=x_B_C_T_H_W.device)
            else:
                padding_mask = transforms.functional.resize(padding_mask, list(x_B_C_T_H_W.shape[-2:]), interpolation=transforms.InterpolationMode.NEAREST)
            x_B_C_T_H_W = torch.cat([x_B_C_T_H_W, padding_mask.unsqueeze(1).repeat(1, 1, x_B_C_T_H_W.shape[2], 1, 1)], dim=1)
        x_B_T_H_W_D = self.x_embedder(x_B_C_T_H_W)
        if self.extra_per_block_abs_pos_emb:
            extra_pos_emb = self.extra_pos_embedder(x_B_T_H_W_D, fps=fps, device=x_B_C_T_H_W.device, dtype=x_B_C_T_H_W.dtype)
        else:
            extra_pos_emb = None
        if 'rope' in self.pos_emb_cls.lower():
            return (x_B_T_H_W_D, self.pos_embedder(x_B_T_H_W_D, fps=fps, device=x_B_C_T_H_W.device), extra_pos_emb)
        x_B_T_H_W_D = x_B_T_H_W_D + self.pos_embedder(x_B_T_H_W_D, device=x_B_C_T_H_W.device)
        return (x_B_T_H_W_D, None, extra_pos_emb)

    def unpatchify(self, x_B_T_H_W_M: torch.Tensor) -> torch.Tensor:
        x_B_C_Tt_Hp_Wp = rearrange(x_B_T_H_W_M, 'B T H W (p1 p2 t C) -> B C (T t) (H p1) (W p2)', p1=self.patch_spatial, p2=self.patch_spatial, t=self.patch_temporal)
        return x_B_C_Tt_Hp_Wp

    def forward(self, x: torch.Tensor, timesteps: torch.Tensor, context: torch.Tensor, fps: Optional[torch.Tensor]=None, padding_mask: Optional[torch.Tensor]=None, **kwargs):
        return comfy.patcher_extension.WrapperExecutor.new_class_executor(self._forward, self, comfy.patcher_extension.get_all_wrappers(comfy.patcher_extension.WrappersMP.DIFFUSION_MODEL, kwargs.get('transformer_options', {}))).execute(x, timesteps, context, fps, padding_mask, **kwargs)

    def _forward(self, x: torch.Tensor, timesteps: torch.Tensor, context: torch.Tensor, fps: Optional[torch.Tensor]=None, padding_mask: Optional[torch.Tensor]=None, **kwargs):
        orig_shape = list(x.shape)
        x = comfy.ldm.common_dit.pad_to_patch_size(x, (self.patch_temporal, self.patch_spatial, self.patch_spatial))
        x_B_C_T_H_W = x
        timesteps_B_T = timesteps
        crossattn_emb = context
        '\n        Args:\n            x: (B, C, T, H, W) tensor of spatial-temp inputs\n            timesteps: (B, ) tensor of timesteps\n            crossattn_emb: (B, N, D) tensor of cross-attention embeddings\n        '
        (x_B_T_H_W_D, rope_emb_L_1_1_D, extra_pos_emb_B_T_H_W_D_or_T_H_W_B_D) = self.prepare_embedded_sequence(x_B_C_T_H_W, fps=fps, padding_mask=padding_mask)
        if timesteps_B_T.ndim == 1:
            timesteps_B_T = timesteps_B_T.unsqueeze(1)
        (t_embedding_B_T_D, adaln_lora_B_T_3D) = self.t_embedder[1](self.t_embedder[0](timesteps_B_T).to(x_B_T_H_W_D.dtype))
        t_embedding_B_T_D = self.t_embedding_norm(t_embedding_B_T_D)
        affline_scale_log_info = {}
        affline_scale_log_info['t_embedding_B_T_D'] = t_embedding_B_T_D.detach()
        self.affline_scale_log_info = affline_scale_log_info
        self.affline_emb = t_embedding_B_T_D
        self.crossattn_emb = crossattn_emb
        if extra_pos_emb_B_T_H_W_D_or_T_H_W_B_D is not None:
            assert x_B_T_H_W_D.shape == extra_pos_emb_B_T_H_W_D_or_T_H_W_B_D.shape, f'{x_B_T_H_W_D.shape} != {extra_pos_emb_B_T_H_W_D_or_T_H_W_B_D.shape}'
        block_kwargs = {'rope_emb_L_1_1_D': rope_emb_L_1_1_D.unsqueeze(1).unsqueeze(0), 'adaln_lora_B_T_3D': adaln_lora_B_T_3D, 'extra_per_block_pos_emb': extra_pos_emb_B_T_H_W_D_or_T_H_W_B_D, 'transformer_options': kwargs.get('transformer_options', {})}
        if x_B_T_H_W_D.dtype == torch.float16:
            x_B_T_H_W_D = x_B_T_H_W_D.float()
        for block in self.blocks:
            x_B_T_H_W_D = block(x_B_T_H_W_D, t_embedding_B_T_D, crossattn_emb, **block_kwargs)
        x_B_T_H_W_O = self.final_layer(x_B_T_H_W_D.to(crossattn_emb.dtype), t_embedding_B_T_D, adaln_lora_B_T_3D=adaln_lora_B_T_3D)
        x_B_C_Tt_Hp_Wp = self.unpatchify(x_B_T_H_W_O)[:, :, :orig_shape[-3], :orig_shape[-2], :orig_shape[-1]]
        return x_B_C_Tt_Hp_Wp