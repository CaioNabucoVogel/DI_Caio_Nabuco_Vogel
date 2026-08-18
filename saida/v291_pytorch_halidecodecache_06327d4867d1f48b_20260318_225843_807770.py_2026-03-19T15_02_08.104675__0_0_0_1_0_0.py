@staticmethod
@functools.cache
def find_header(name: str) -> str:
    if 'HALIDE_INCLUDE' in os.environ:
        path = os.path.join(os.environ['HALIDE_INCLUDE'], name)
        if os.path.exists(path):
            return path
    if 'HALIDE_LIB' in os.environ:
        path = os.path.abspath(os.path.join(os.environ['HALIDE_LIB'], f'../include/{name}'))
        if os.path.exists(path):
            return path
    errmsg = f"Can't find {name}, set env HALIDE_INCLUDE to the directory containing it"
    return HalideCodeCache._search_for_file(f'../include/{name}', errmsg)