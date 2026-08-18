class HalideCodeCache(CppPythonBindingsCodeCache):
    cache: dict[str, Callable[[], ModuleType | CDLL]] = {}
    cache_clear = staticmethod(cache.clear)
    _standalone_runtime_path: str | None = None
    prefix = textwrap.dedent('\n        #include "{halideruntime_h}"\n        #include "{headerfile}"\n        #include <stdexcept>\n        #include <cmath>\n\n        namespace c10 {{\n            inline long div_floor_integer(long a, long b) {{\n                if ((a<0) != (b<0)) {{\n                    const auto quot = a / b;\n                    const auto rem = a % b;\n                    return rem ? quot - 1 : quot;\n                }}\n                return a / b;\n            }}\n        }}\n        ')
    glue_template_cpp = prefix + textwrap.dedent('\n        void kernel({argdefs}) {{\n            {buffers}\n            int err = halide_kernel({buffer_names});\n            if(err != 0) throw std::runtime_error("halide_kernel failed");\n        }}\n        ')
    glue_template_cuda = prefix + textwrap.dedent('\n        #include <cuda.h>\n        static const halide_device_interface_t* cuda_interface = halide_cuda_device_interface();\n\n        void kernel({argdefs}, uintptr_t stream) {{\n            {buffers}\n            int err = halide_kernel(reinterpret_cast<void*>(stream), {buffer_names});\n            if(err != 0) throw std::runtime_error("halide_kernel failed");\n        }}\n        ')
    standalone_runtime_cuda_init = textwrap.dedent('\n        #include "{}"\n        #include <cuda.h>\n\n        static int acquire_context(void* user_context,\n                                   void** cuda_context_out,\n                                   bool create) {{\n            return cuCtxGetCurrent(reinterpret_cast<CUcontext*>(cuda_context_out));\n        }}\n\n        static int release_context(void* user_context) {{\n            return 0;\n        }}\n\n        static int get_stream(void* user_context,\n                              void* cuda_context,\n                              void** stream_out) {{\n            *stream_out = user_context;\n            return 0;\n        }}\n\n        static int register_halide_hooks() {{\n            halide_set_cuda_acquire_context(&acquire_context);\n            halide_set_cuda_release_context(&release_context);\n            halide_set_cuda_get_stream(&get_stream);\n            return 0;\n        }}\n\n        int inductor_register_halide_hooks_result = register_halide_hooks();\n        ')

    @classmethod
    def _codegen_buffer(cls, name: str, arg: HalideInputSpec, cuda: bool) -> list[str]:
        assert arg.shape is not None
        assert arg.stride is not None and len(arg.shape) == len(arg.stride)
        assert arg.offset is not None
        data_ptr = f'{arg.alias_of or arg.name} + {arg.offset}'
        if cuda:
            device = f'reinterpret_cast<uint64_t>({data_ptr})'
            device_interface = 'cuda_interface'
            host = 'nullptr'
            flags = 'halide_buffer_flag_device_dirty'
        else:
            device = '0'
            device_interface = 'nullptr'
            host = f'reinterpret_cast<uint8_t*>({data_ptr})'
            flags = 'halide_buffer_flag_host_dirty'
        dims = []
        for (size, stride) in zip(arg.shape, arg.stride):
            dims.append(f'halide_dimension_t(0, {size}, {stride})')
        return [f'halide_buffer_t {name};', f"halide_dimension_t {name}_dims[] = {{{', '.join(dims)}}};" if len(dims) > 0 else f'halide_dimension_t * {name}_dims = nullptr;', f'{name}.device = {device};', f'{name}.device_interface = {device_interface};', f'{name}.host = {host};', f'{name}.flags = {flags};', f'{name}.type = {arg.halide_type()};', f'{name}.dimensions = {len(dims)};', f'{name}.dim = {name}_dims;', f'{name}.padding = nullptr;']

    @classmethod
    def _codegen_glue(cls, meta: HalideMeta, headerfile: object) -> str:
        is_cuda = meta.is_cuda()
        assert is_cuda is ('user_context' in meta.target)
        assert 'no_runtime' in meta.target
        buffers = []
        buffer_names = []
        for (i, arg) in enumerate(meta.argtypes):
            if arg.is_buffer():
                buffer_names.append(f'&hl_buf_{i}')
                buffers.extend(cls._codegen_buffer(f'hl_buf_{i}', arg, is_cuda))
            else:
                assert '*' not in arg.ctype
                buffer_names.append(arg.name)
        buffers = '\n'.join([f'    {line}' for line in buffers]).lstrip()
        glue_template = cls.glue_template_cuda if is_cuda else cls.glue_template_cpp
        glue_code = glue_template.format(halideruntime_h=cls.find_header('HalideRuntimeCuda.h' if is_cuda else 'HalideRuntime.h'), headerfile=headerfile, argdefs=', '.join((f'{a.bindings_type()} {a.name}' for a in meta.argtypes if a.alias_of is None)), buffers=buffers, buffer_names=', '.join(buffer_names))
        return glue_code

    @classmethod
    @functools.cache
    def config_hash(cls) -> str:
        command_gen = CppBuilder(name='O', sources='I', BuildOption=CppOptions())
        command_line = command_gen.get_command_line()
        return sha256_hash('\n'.join([cls.glue_template_cpp, cls.glue_template_cuda, cls.standalone_runtime_cuda_init, command_line]).encode('utf-8'))

    @staticmethod
    def _search_for_file(suffix: str, errmsg: str) -> str:
        spec = importlib.machinery.PathFinder.find_spec('halide')
        if spec is None or not spec.submodule_search_locations:
            raise RuntimeError('halide python bindings not installed')
        try:
            search = spec.submodule_search_locations[0]
            for file in os.listdir(search):
                if file.endswith('.so'):
                    try:
                        out = subprocess.check_output(['ldd', os.path.join(search, file)])
                    except subprocess.SubprocessError:
                        continue
                    m = re.search('(/.*)/libHalide.so', out.decode('utf-8'))
                    if m:
                        path = os.path.join(os.path.abspath(m.group(1)), suffix)
                        if os.path.exists(path):
                            return os.path.abspath(path)
        except Exception as e:
            raise RuntimeError(errmsg) from e
        raise RuntimeError(errmsg)

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

    @classmethod
    def generate_halide_async(cls, meta: HalideMeta, source_code: str, submit_fn: Any=None) -> Callable[[], Any]:
        dirpath = Path(get_path(code_hash(source_code, extra=repr((cls.config_hash(), meta))), 'halide')[2])
        os.makedirs(dirpath, exist_ok=True)
        wait_for_compile = None
        genfile = str(dirpath / 'generate_kernel.py')
        libfile = str(dirpath / 'halide_kernel.a')
        headerfile = str(dirpath / 'halide_kernel.h')
        donefile = str(dirpath / 'done')
        lockfile = str(dirpath / 'lock')
        need_compile = not os.path.exists(donefile)
        jobs: list[Any] = []
        if need_compile:
            write_atomic(genfile, source_code)
            cmd = [sys.executable, genfile, '-g', 'kernel', '-o', f'{dirpath}', '-f', 'halide_kernel', '-e', 'static_library,h,schedule']
            if meta.scheduler:
                cmd.extend(['-p', cls.find_libautoschedule(meta.scheduler)])
            cmd.extend(meta.args())
            jobs.append(functools.partial(subprocess.check_call, cmd))
        binding_types = [arg.bindings_type() for arg in meta.argtypes if arg.alias_of is None]
        if meta.is_cuda():
            binding_types.append('uintptr_t')
        bindings_future = cls.load_pybinding_async(binding_types, cls._codegen_glue(meta, headerfile), extra_flags=(libfile, cls.build_standalone_runtime()), submit_fn=jobs.append if need_compile else None, device_type='cuda' if meta.is_cuda() else 'cpu')
        if need_compile:
            jobs.append(functools.partial(touch, donefile))
            task = functools.partial(_worker_task_halide, lockfile, jobs)
            if submit_fn:
                wait_for_compile = submit_fn(task).result
            else:
                task()

        def load() -> Callable[[], Any]:
            if wait_for_compile:
                wait_for_compile()
            return bindings_future()
        return load

    @classmethod
    def generate_halide(cls, *args: Any, **kwargs: Any) -> Callable[[], Any]:
        return cls.generate_halide_async(*args, **kwargs)()

    @classmethod
    def build_standalone_runtime(cls) -> str:
        if cls._standalone_runtime_path and os.path.exists(cls._standalone_runtime_path):
            return cls._standalone_runtime_path
        device_type = 'cuda' if torch.cuda.is_available() else 'cpu'
        libname = 'libStandaloneHalideRuntime.so'
        target = 'host-cuda' if device_type == 'cuda' else 'host'
        if cls._standalone_runtime_path:
            assert not os.path.exists(cls._standalone_runtime_path)
            base = default_cache_dir()
        else:
            base = cache_dir()
        dirpath = Path(base) / f'halide-runtime-{target}-{cls.config_hash()}'
        os.makedirs(dirpath, exist_ok=True)
        done_file = str(dirpath / 'done')
        lock_file = str(dirpath / 'lock')
        hook_file = str(dirpath / 'hooks.cpp')
        a_file = str(dirpath / 'standalone_halide_runtime.a')
        so_file = str(dirpath / libname)
        if not os.path.exists(done_file):
            import halide as hl
            from torch.utils._filelock import FileLock
            with FileLock(lock_file, LOCK_TIMEOUT):
                if not os.path.exists(done_file):
                    with open(hook_file, 'w') as f:
                        if device_type == 'cuda':
                            f.write(cls.standalone_runtime_cuda_init.format(cls.find_header('HalideRuntimeCuda.h')))
                    hl.compile_standalone_runtime(a_file, hl.Target(target))
                    (name, output_dir) = get_name_and_dir_from_output_file_path(so_file)
                    halide_cmd_gen = CppBuilder(name=name, sources=[hook_file, a_file], output_dir=output_dir, BuildOption=CppTorchDeviceOptions(device_type=device_type))
                    subprocess.check_call(shlex.split(halide_cmd_gen.get_command_line()))
                    touch(done_file)
        assert os.path.exists(so_file)
        cls._standalone_runtime_path = so_file
        return so_file

    @classmethod
    def _get_uncompiled_header(cls, device: str) -> str | None:
        """Header precompiling is currently disabled for halide."""
        return None