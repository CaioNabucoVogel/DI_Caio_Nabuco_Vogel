def execute(cls, clip, tags, lyrics, lyrics_strength) -> io.NodeOutput:
    tokens = clip.tokenize(tags, lyrics=lyrics)
    conditioning = clip.encode_from_tokens_scheduled(tokens)
    conditioning = node_helpers.conditioning_set_values(conditioning, {'lyrics_strength': lyrics_strength})
    return io.NodeOutput(conditioning)