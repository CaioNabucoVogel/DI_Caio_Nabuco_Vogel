class LoRARequestStates:
    """A per-LoRA count of running and waiting requests."""

    def __init__(self, log_stats: bool=False):
        self.log_stats = log_stats
        self.requests: defaultdict[str, LoRAStats] = defaultdict(LoRAStats)

    def _request_update(self, req_id: str, lora_name: str | None, waiting: bool, running: bool):
        if not self.log_stats or lora_name is None:
            return
        lora_stats = self.requests[lora_name]
        lora_stats.update(req_id, waiting, running)
        if lora_stats.empty:
            del self.requests[lora_name]

    def request_waiting(self, req_id: str, lora_name: str | None):
        self._request_update(req_id, lora_name, waiting=True, running=False)

    def request_running(self, req_id: str, lora_name: str | None):
        self._request_update(req_id, lora_name, waiting=False, running=True)

    def request_finished(self, req_id: str, lora_name: str | None):
        self._request_update(req_id, lora_name, waiting=False, running=False)

    def update_scheduler_stats(self, scheduler_stats: SchedulerStats | None):
        if not self.log_stats or scheduler_stats is None:
            return
        for (lora_name, stats) in self.requests.items():
            scheduler_stats.waiting_lora_adapters[lora_name] = len(stats.waiting)
            scheduler_stats.running_lora_adapters[lora_name] = len(stats.running)