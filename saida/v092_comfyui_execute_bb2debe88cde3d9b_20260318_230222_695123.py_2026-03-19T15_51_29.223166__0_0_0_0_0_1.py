def execute(cls, *, width: int, height: int, batch_size: int=1) -> io.NodeOutput:
    latent = torch.zeros((batch_size, 3, height, width), device=comfy.model_management.intermediate_device())
    return io.NodeOutput({'samples': latent})