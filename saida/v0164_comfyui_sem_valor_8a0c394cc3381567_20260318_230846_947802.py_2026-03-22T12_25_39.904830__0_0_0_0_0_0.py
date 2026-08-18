def __init__(self, model_config, model_type=ModelType.FLOW, image_to_video=False, device=None):
    super(WAN21, self).__init__(model_config, model_type, device=device, unet_model=comfy.ldm.wan.model.CameraWanModel)
    self.image_to_video = image_to_video