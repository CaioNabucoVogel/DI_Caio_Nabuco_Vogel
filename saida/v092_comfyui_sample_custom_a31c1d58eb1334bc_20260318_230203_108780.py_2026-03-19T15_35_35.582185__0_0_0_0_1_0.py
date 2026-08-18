def sample_custom(model, noise, cfg, sampler, sigmas, positive, negative, latent_image, noise_mask=None, callback=None, disable_pbar=False, seed=None):
    samples = comfy.samplers.sample(model, noise, positive, negative, cfg, model.load_device, sampler, sigmas, model_options=model.model_options, latent_image=latent_image, denoise_mask=noise_mask, callback=callback, disable_pbar=disable_pbar, seed=seed)
    samples = samples.to(comfy.model_management.intermediate_device())
    return samples