def maybe_test_cache(code: str, extra: str, kernel):
    if self.test_cache or self.debug:
        with patch.object(V.graph, 'get_dtype', self._fake_get_dtype(fake_out)), V.graph.set_current_device(layout.device), make_kernel() as kernel_test:
            result2 = generate_code(kernel_test)
            assert result2 is not None
            (code_test, extra_test) = result2
            assert code == code_test and extra == extra_test and (kernel.args.input_buffers == kernel_test.args.input_buffers) and (kernel.prologue_supported_inputs == kernel_test.prologue_supported_inputs) and (kernel.args.sizevars == kernel_test.args.sizevars), 'Generated code cache results in wrong output'