def execute(cls, positive, vae, width, height, length, batch_size, guidance_type, start_image=None) -> io.NodeOutput:
    latent = torch.zeros([batch_size, 16, (length - 1) // 4 + 1, height // 8, width // 8], device=comfy.model_management.intermediate_device())
    out_latent = {}
    if start_image is not None:
        start_image = comfy.utils.common_upscale(start_image[:length, :, :, :3].movedim(-1, 1), width, height, 'bilinear', 'center').movedim(1, -1)
        concat_latent_image = vae.encode(start_image)
        mask = torch.ones((1, 1, latent.shape[2], concat_latent_image.shape[-2], concat_latent_image.shape[-1]), device=start_image.device, dtype=start_image.dtype)
        mask[:, :, :(start_image.shape[0] - 1) // 4 + 1] = 0.0
        if guidance_type == 'v1 (concat)':
            cond = {'concat_latent_image': concat_latent_image, 'concat_mask': mask}
        elif guidance_type == 'v2 (replace)':
            cond = {'guiding_frame_index': 0}
            latent[:, :, :concat_latent_image.shape[2]] = concat_latent_image
            out_latent['noise_mask'] = mask
        elif guidance_type == 'custom':
            cond = {'ref_latent': concat_latent_image}
        positive = node_helpers.conditioning_set_values(positive, cond)
    out_latent['samples'] = latent
    return io.NodeOutput(positive, out_latent)