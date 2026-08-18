def execute(cls, string_a, string_b, mode, case_sensitive):
    if case_sensitive:
        a = string_a
        b = string_b
    else:
        a = string_a.lower()
        b = string_b.lower()
    if mode == 'Equal':
        return io.NodeOutput(a == b)
    elif mode == 'Starts With':
        return io.NodeOutput(a.startswith(b))
    elif mode == 'Ends With':
        return io.NodeOutput(a.endswith(b))