def __init__(self, patch_size: int, sample_rate=16000, hop_length=160, audio_latent_downsample_factor=4, is_causal=True, start_end=False, shift=0):
    super().__init__(patch_size, start_end=start_end)
    self.hop_length = hop_length
    self.sample_rate = sample_rate
    self.audio_latent_downsample_factor = audio_latent_downsample_factor
    self.is_causal = is_causal
    self.shift = shift