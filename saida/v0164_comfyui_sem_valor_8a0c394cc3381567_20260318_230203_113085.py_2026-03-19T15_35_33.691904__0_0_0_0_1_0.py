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