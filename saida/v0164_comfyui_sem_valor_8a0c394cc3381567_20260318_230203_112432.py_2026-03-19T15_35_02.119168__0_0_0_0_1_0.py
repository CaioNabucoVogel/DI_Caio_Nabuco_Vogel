def execute(cls, audio, low_gain_dB, low_freq, mid_gain_dB, mid_freq, mid_q, high_gain_dB, high_freq) -> IO.NodeOutput:
    waveform = audio['waveform']
    sample_rate = audio['sample_rate']
    eq_waveform = waveform.clone()
    if low_gain_dB != 0:
        eq_waveform = torchaudio.functional.bass_biquad(eq_waveform, sample_rate, gain=low_gain_dB, central_freq=float(low_freq), Q=0.707)
    if mid_gain_dB != 0:
        eq_waveform = torchaudio.functional.equalizer_biquad(eq_waveform, sample_rate, center_freq=float(mid_freq), gain=mid_gain_dB, Q=mid_q)
    if high_gain_dB != 0:
        eq_waveform = torchaudio.functional.treble_biquad(eq_waveform, sample_rate, gain=high_gain_dB, central_freq=float(high_freq), Q=0.707)
    return IO.NodeOutput({'waveform': eq_waveform, 'sample_rate': sample_rate})