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