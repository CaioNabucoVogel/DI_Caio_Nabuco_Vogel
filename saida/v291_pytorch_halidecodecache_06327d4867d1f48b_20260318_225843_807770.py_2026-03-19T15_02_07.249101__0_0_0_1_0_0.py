@staticmethod
@functools.cache
def find_libautoschedule(name: str) -> str:
    sofile = f'libautoschedule_{name.lower()}.so'
    if 'HALIDE_LIB' in os.environ:
        path = os.path.join(os.environ['HALIDE_LIB'], sofile)
        if os.path.exists(path):
            return path
    errmsg = f"Can't find {sofile}, set env HALIDE_LIB to the directory containing it"
    return HalideCodeCache._search_for_file(sofile, errmsg)