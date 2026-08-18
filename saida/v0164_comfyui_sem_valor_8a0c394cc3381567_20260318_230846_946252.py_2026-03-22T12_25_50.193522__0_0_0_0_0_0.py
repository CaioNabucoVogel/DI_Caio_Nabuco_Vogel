def execute(cls, positive, negative, seconds_start, seconds_total) -> IO.NodeOutput:
    positive = node_helpers.conditioning_set_values(positive, {'seconds_start': seconds_start, 'seconds_total': seconds_total})
    negative = node_helpers.conditioning_set_values(negative, {'seconds_start': seconds_start, 'seconds_total': seconds_total})
    return IO.NodeOutput(positive, negative)