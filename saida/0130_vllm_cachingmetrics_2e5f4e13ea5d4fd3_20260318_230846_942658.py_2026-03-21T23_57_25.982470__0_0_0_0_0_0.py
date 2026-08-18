class CachingMetrics:
    """Metrics for caching with a hit rate of the most recent N requests.
    Args:
        interval: The number of the most recent requests to aggregate.
            Defaults to 1000.
    """

    def __init__(self, max_recent_requests: int=1000) -> None:
        super().__init__()
        self.max_recent_requests = max_recent_requests
        self.aggregated_requests = 0
        self.aggregated_query_total = 0
        self.aggregated_query_hit = 0
        self.query_queue = deque[tuple[int, int, int]]()

    def observe(self, stats: BaseCacheStats):
        """Observe the prefix caching for a set of requests.

        This function is called with information gathered when new requests
        are being scheduled and are looking for computed blocks.

        When there are more than `max_recent_requests` requests, the oldest set
        of requests are removed from the metrics.

        Args:
            stats: The prefix cache stats.
        """
        if stats.reset:
            self.reset()
        if stats.requests == 0:
            return
        self.query_queue.append((stats.requests, stats.queries, stats.hits))
        self.aggregated_requests += stats.requests
        self.aggregated_query_total += stats.queries
        self.aggregated_query_hit += stats.hits
        while len(self.query_queue) > 1 and self.aggregated_requests > self.max_recent_requests:
            (old_requests, old_queries, old_hits) = self.query_queue.popleft()
            self.aggregated_requests -= old_requests
            self.aggregated_query_total -= old_queries
            self.aggregated_query_hit -= old_hits

    def reset(self):
        """Reset the metrics."""
        self.aggregated_requests = 0
        self.aggregated_query_total = 0
        self.aggregated_query_hit = 0
        self.query_queue.clear()

    @property
    def empty(self) -> bool:
        """Return true if no requests have been observed."""
        return self.aggregated_requests == 0

    @property
    def hit_rate(self) -> float:
        """Calculate the hit rate for the past N requests."""
        if self.aggregated_query_total == 0:
            return 0.0
        return self.aggregated_query_hit / self.aggregated_query_total