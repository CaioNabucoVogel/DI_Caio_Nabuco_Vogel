def execute(cls, model) -> io.NodeOutput:
    m = model.clone()

    def cfg_zero_star(args):
        guidance_scale = args['cond_scale']
        x = args['input']
        cond_p = args['cond_denoised']
        uncond_p = args['uncond_denoised']
        out = args['denoised']
        alpha = optimized_scale(x - cond_p, x - uncond_p)
        return out + uncond_p * (alpha - 1.0) + guidance_scale * uncond_p * (1.0 - alpha)
    m.set_model_sampler_post_cfg_function(cfg_zero_star)
    return io.NodeOutput(m)