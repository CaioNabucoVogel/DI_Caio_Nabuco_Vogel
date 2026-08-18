def execute(cls, destination, source, x, y, resize_source, mask=None) -> IO.NodeOutput:
    (destination, source) = node_helpers.image_alpha_fix(destination, source)
    destination = destination.clone().movedim(-1, 1)
    output = composite(destination, source.movedim(-1, 1), x, y, mask, 1, resize_source).movedim(1, -1)
    return IO.NodeOutput(output)