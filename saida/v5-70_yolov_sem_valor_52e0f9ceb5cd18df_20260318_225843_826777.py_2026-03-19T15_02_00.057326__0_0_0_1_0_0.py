def masks(self, masks, colors, im_gpu=None, alpha=0.5):
    """Plot masks at once.
        Args:
            masks (tensor): predicted masks on cuda, shape: [n, h, w]
            colors (List[List[Int]]): colors for predicted masks, [[r, g, b] * n]
            im_gpu (tensor): img is in cuda, shape: [3, h, w], range: [0, 1]
            alpha (float): mask transparency: 0.0 fully transparent, 1.0 opaque
        """
    if self.pil:
        self.im = np.asarray(self.im).copy()
    if im_gpu is None:
        if len(masks) == 0:
            return
        if isinstance(masks, torch.Tensor):
            masks = torch.as_tensor(masks, dtype=torch.uint8)
            masks = masks.permute(1, 2, 0).contiguous()
            masks = masks.cpu().numpy()
        masks = scale_image(masks.shape[:2], masks, self.im.shape)
        masks = np.asarray(masks, dtype=np.float32)
        colors = np.asarray(colors, dtype=np.float32)
        s = masks.sum(2, keepdims=True).clip(0, 1)
        masks = (masks @ colors).clip(0, 255)
        self.im[:] = masks * alpha + self.im * (1 - s * alpha)
    else:
        if len(masks) == 0:
            self.im[:] = im_gpu.permute(1, 2, 0).contiguous().cpu().numpy() * 255
        colors = torch.tensor(colors, device=im_gpu.device, dtype=torch.float32) / 255.0
        colors = colors[:, None, None]
        masks = masks.unsqueeze(3)
        masks_color = masks * (colors * alpha)
        inv_alph_masks = (1 - masks * alpha).cumprod(0)
        mcs = (masks_color * inv_alph_masks).sum(0) * 2
        im_gpu = im_gpu.flip(dims=[0])
        im_gpu = im_gpu.permute(1, 2, 0).contiguous()
        im_gpu = im_gpu * inv_alph_masks[-1] + mcs
        im_mask = (im_gpu * 255).byte().cpu().numpy()
        self.im[:] = scale_image(im_gpu.shape, im_mask, self.im.shape)
    if self.pil:
        self.fromarray(self.im)