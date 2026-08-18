def unpatchify(self, x_B_T_H_W_M: torch.Tensor) -> torch.Tensor:
    x_B_C_Tt_Hp_Wp = rearrange(x_B_T_H_W_M, 'B T H W (p1 p2 t C) -> B C (T t) (H p1) (W p2)', p1=self.patch_spatial, p2=self.patch_spatial, t=self.patch_temporal)
    return x_B_C_Tt_Hp_Wp