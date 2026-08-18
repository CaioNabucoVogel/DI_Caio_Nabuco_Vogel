def linenumbers(value, autoescape=True):
    """Display text with line numbers."""
    lines = value.split('\n')
    width = str(len(str(len(lines))))
    if not autoescape or isinstance(value, SafeData):
        for (i, line) in enumerate(lines):
            lines[i] = ('%0' + width + 'd. %s') % (i + 1, line)
    else:
        for (i, line) in enumerate(lines):
            lines[i] = ('%0' + width + 'd. %s') % (i + 1, escape(line))
    return mark_safe('\n'.join(lines))