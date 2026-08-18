class LogInterceptor(io.TextIOWrapper):

    def __init__(self, stream, *args, **kwargs):
        buffer = stream.buffer
        encoding = stream.encoding
        super().__init__(buffer, *args, **kwargs, encoding=encoding, line_buffering=stream.line_buffering)
        self._lock = threading.Lock()
        self._flush_callbacks = []
        self._logs_since_flush = []

    def write(self, data):
        entry = {'t': datetime.now().isoformat(), 'm': data}
        with self._lock:
            self._logs_since_flush.append(entry)
            if isinstance(data, str) and data.startswith('\r') and (not logs[-1]['m'].endswith('\n')):
                logs.pop()
            logs.append(entry)
        super().write(data)

    def flush(self):
        super().flush()
        for cb in self._flush_callbacks:
            cb(self._logs_since_flush)
            self._logs_since_flush = []

    def on_flush(self, callback):
        self._flush_callbacks.append(callback)