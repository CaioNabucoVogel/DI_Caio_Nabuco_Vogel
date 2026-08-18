@classmethod
@functools.cache
def config_hash(cls) -> str:
    command_gen = CppBuilder(name='O', sources='I', BuildOption=CppOptions())
    command_line = command_gen.get_command_line()
    return sha256_hash('\n'.join([cls.glue_template_cpp, cls.glue_template_cuda, cls.standalone_runtime_cuda_init, command_line]).encode('utf-8'))