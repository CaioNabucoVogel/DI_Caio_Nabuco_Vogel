class IterationStats:
    """Stats associated with a single set of EngineCoreOutputs."""

    def __init__(self):
        self.iteration_timestamp = time.time()
        self.num_generation_tokens = 0
        self.num_prompt_tokens = 0
        self.num_preempted_reqs = 0
        self.finished_requests: list[FinishedRequestStats] = []
        self.max_num_generation_tokens_iter: list[int] = []
        self.n_params_iter: list[int] = []
        self.time_to_first_tokens_iter: list[float] = []
        self.inter_token_latencies_iter: list[float] = []
        self.num_corrupted_reqs: int = 0

    def __repr__(self) -> str:
        field_to_value_str = ', '.join((f'{k}={v}' for (k, v) in vars(self).items()))
        return f'{self.__class__.__name__}({field_to_value_str})'

    def _time_since(self, start: float) -> float:
        """Calculate an interval relative to this iteration's timestamp."""
        return self.iteration_timestamp - start

    def update_from_output(self, output: 'EngineCoreOutput', engine_core_timestamp: float, is_prefilling: bool, prompt_len: int, req_stats: RequestStateStats, lora_states: 'LoRARequestStates', lora_name: str | None):
        num_new_generation_tokens = len(output.new_token_ids)
        self.num_generation_tokens += num_new_generation_tokens
        if is_prefilling:
            self.num_prompt_tokens += prompt_len
            first_token_latency = self._time_since(req_stats.arrival_time)
            self.time_to_first_tokens_iter.append(first_token_latency)
            req_stats.first_token_latency = first_token_latency
        req_stats.num_generation_tokens += num_new_generation_tokens
        if envs.VLLM_COMPUTE_NANS_IN_LOGITS and (not req_stats.is_corrupted) and (output.num_nans_in_logits > 0):
            req_stats.is_corrupted = True
        if output.events is not None:
            self.update_from_events(output.request_id, output.events, is_prefilling, req_stats, lora_states, lora_name)
        if is_prefilling:
            req_stats.first_token_ts = engine_core_timestamp
        else:
            itl = engine_core_timestamp - req_stats.last_token_ts
            self.inter_token_latencies_iter.append(itl)
        req_stats.last_token_ts = engine_core_timestamp

    def update_from_events(self, req_id: str, events: list['EngineCoreEvent'], is_prefilling: bool, req_stats: RequestStateStats, lora_states: 'LoRARequestStates', lora_name: str | None):
        from vllm.v1.engine import EngineCoreEventType
        for event in events:
            if event.type == EngineCoreEventType.QUEUED:
                req_stats.queued_ts = event.timestamp
                lora_states.request_waiting(req_id, lora_name)
            elif event.type == EngineCoreEventType.SCHEDULED:
                if req_stats.scheduled_ts == 0.0:
                    req_stats.scheduled_ts = event.timestamp
                lora_states.request_running(req_id, lora_name)
            elif event.type == EngineCoreEventType.PREEMPTED:
                self.num_preempted_reqs += 1
                lora_states.request_waiting(req_id, lora_name)

    def update_from_finished_request(self, finish_reason: 'FinishReason', num_prompt_tokens: int, max_tokens_param: int | None, req_stats: RequestStateStats, num_cached_tokens: int=0):
        e2e_latency = self._time_since(req_stats.arrival_time)
        queued_time = req_stats.scheduled_ts - req_stats.queued_ts
        prefill_time = req_stats.first_token_ts - req_stats.scheduled_ts
        decode_time = req_stats.last_token_ts - req_stats.first_token_ts
        inference_time = req_stats.last_token_ts - req_stats.scheduled_ts
        mean_time_per_output_token = decode_time / (req_stats.num_generation_tokens - 1) if req_stats.num_generation_tokens - 1 > 0 else 0
        finished_req = FinishedRequestStats(finish_reason=finish_reason, e2e_latency=e2e_latency, num_prompt_tokens=num_prompt_tokens, num_generation_tokens=req_stats.num_generation_tokens, max_tokens_param=max_tokens_param, queued_time=queued_time, prefill_time=prefill_time, inference_time=inference_time, decode_time=decode_time, mean_time_per_output_token=mean_time_per_output_token, is_corrupted=req_stats.is_corrupted, num_cached_tokens=num_cached_tokens)
        self.finished_requests.append(finished_req)
        if req_stats.is_corrupted:
            self.num_corrupted_reqs += 1