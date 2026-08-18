def __init__(self, device='cpu', max_length=77, freeze=True, layer='penultimate', layer_idx=None, dtype=None, model_options={}):
    if layer == 'penultimate':
        layer = 'hidden'
        layer_idx = -2
    textmodel_json_config = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'clip_config_bigg.json')
    model_options = {**model_options, 'model_name': 'clip_g'}
    super().__init__(device=device, freeze=freeze, layer=layer, layer_idx=layer_idx, textmodel_json_config=textmodel_json_config, dtype=dtype, special_tokens={'start': 49406, 'end': 49407, 'pad': 0}, layer_norm_hidden_state=False, return_projected_pooled=True, model_options=model_options)