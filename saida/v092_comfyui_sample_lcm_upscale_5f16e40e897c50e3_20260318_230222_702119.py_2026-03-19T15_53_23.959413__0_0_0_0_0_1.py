def sample_lcm_upscale(model, x, sigmas, extra_args=None, callback=None, disable=None, total_upscale=2.0, upscale_method='bislerp', upscale_steps=None):
    extra_args = {} if extra_args is None else extra_args
    if upscale_steps is None:
        upscale_steps = max(len(sigmas) // 2 + 1, 2)
    else:
        upscale_steps += 1
        upscale_steps = min(upscale_steps, len(sigmas) + 1)
    upscales = np.linspace(1.0, total_upscale, upscale_steps)[1:]
    orig_shape = x.size()
    s_in = x.new_ones([x.shape[0]])
    for i in trange(len(sigmas) - 1, disable=disable):
        denoised = model(x, sigmas[i] * s_in, **extra_args)
        if callback is not None:
            callback({'x': x, 'i': i, 'sigma': sigmas[i], 'sigma_hat': sigmas[i], 'denoised': denoised})
        x = denoised
        if i < len(upscales):
            x = comfy.utils.common_upscale(x, round(orig_shape[-1] * upscales[i]), round(orig_shape[-2] * upscales[i]), upscale_method, 'disabled')
        if sigmas[i + 1] > 0:
            x += sigmas[i + 1] * torch.randn_like(x)
    return x