def prepare_sampling(model, noise_shape, positive, negative, noise_mask):
    logging.warning("Warning: comfy.sample.prepare_sampling isn't used anymore and can be removed")
    return (model, positive, negative, noise_mask, [])