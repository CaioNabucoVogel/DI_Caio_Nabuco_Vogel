@classmethod
def compile(cls, source_code: str, dst_file_ext: str, extra_args: list[str] | None=None) -> tuple[str, str, str]:
    """
        Compiles CUDA source_code into a file with dst_file_ext extension.
        If dst_file_ext is "so", first compiles to ".o" and then links to ".so".
        Returns a tuple of dst_file_path, hash_key, source_code_path
        """
    if dst_file_ext == 'so':
        (obj_path, _, _) = cls.compile(source_code, 'o', extra_args)
        (key, input_path) = cls.write(source_code, dst_file_ext)
        (src_files, operation_name) = ([obj_path], 'Linking')
    else:
        (key, input_path) = cls.write(source_code, dst_file_ext)
        (src_files, operation_name) = ([input_path], 'Compilation')
    key_with_ext = key + dst_file_ext
    if key_with_ext not in cls.cache:
        from torch.utils._filelock import FileLock
        lock_dir = get_lock_dir()
        lock = FileLock(os.path.join(lock_dir, key + '.lock'), timeout=LOCK_TIMEOUT)
        with lock:
            output_path = input_path[:-len(cls._SOURCE_CODE_SUFFIX)] + dst_file_ext
            error_path = binary_error_path(output_path)
            binary_remote_cache = cls.get_kernel_binary_remote_cache(caching_enabled=config.cuda.use_binary_remote_cache and (not config.force_disable_caches), caching_available=config.is_fbcode())
            if binary_remote_cache is not None:
                binary_remote_cache.get(output_path, error_path)
            if os.path.exists(error_path):
                with open(error_path, encoding='utf-8') as fh:
                    error_json = fh.read()
                (cmd_parts, error_output) = json.loads(error_json)
                if binary_remote_cache is not None and config.cuda.upload_to_binary_remote_cache:
                    binary_remote_cache.put(error_path, config.cuda.binary_remote_cache_force_write)
                cls.cache[key_with_ext] = CUDACodeCache.CacheEntry(input_path, output_path, error_json)
                raise exc.CUDACompileError(cmd_parts, error_output)
            if not os.path.exists(output_path):
                cmd = cuda_compile_command(src_files, output_path, dst_file_ext, extra_args)
                with open(input_path, 'a') as f:
                    f.write('\n')
                    f.write(f'// CUDA {operation_name} cmd\n// {cmd}\n')
                start_time = time()
                log.debug('CUDA %s: %s', operation_name, cmd)
                cmd_parts = cmd.split(' ')
                try:
                    if use_re_build():
                        from triton.fb.re_build_helper import run_build_command
                        run_build_command(cmd_parts, os.path.dirname(input_path), os.path.basename(output_path))
                    else:
                        subprocess.check_output(cmd_parts, stderr=subprocess.STDOUT, env=os.environ)
                except subprocess.CalledProcessError as error:
                    cls._record_cuda_compile_error(error.output.decode('utf-8'), key_with_ext, cmd_parts, input_path, output_path, binary_remote_cache)
                    raise exc.CUDACompileError(cmd_parts, error.output) from error
                except Exception as error:
                    if 'COMPILE FAILED WITH' in str(error):
                        cls._record_cuda_compile_error(str(error), key_with_ext, cmd_parts, input_path, output_path, binary_remote_cache)
                        raise exc.CUDACompileError(cmd_parts, str(error)) from error
                    raise error
                end_time = time()
                log_duration_msg = f'CUDA {operation_name} took {end_time - start_time} seconds. Command: {cmd}'
                log.info(log_duration_msg)
            else:
                log.debug('CUDA %s skipped: %s since output already exists', operation_name, output_path)
            if binary_remote_cache is not None and config.cuda.upload_to_binary_remote_cache:
                binary_remote_cache.put(output_path, config.cuda.binary_remote_cache_force_write)
            cls.cache[key_with_ext] = CUDACodeCache.CacheEntry(input_path, output_path, None)
    cache_entry: CUDACodeCache.CacheEntry = cls.cache[key_with_ext]
    if cache_entry.error_json is not None:
        (cmd_parts, error_output) = json.loads(cache_entry.error_json)
        raise exc.CUDACompileError(cmd_parts, error_output.encode('utf-8'))
    return (cls.cache[key_with_ext].output_path, key, input_path)