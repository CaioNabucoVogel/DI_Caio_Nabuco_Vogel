class BrowserError(Exception):
    """Browser error with structured memory for LLM context management.

	This exception class provides separate memory contexts for browser actions:
	- short_term_memory: Immediate context shown once to the LLM for the next action
	- long_term_memory: Persistent error information stored across steps
	"""
    message: str
    short_term_memory: str | None = None
    long_term_memory: str | None = None
    details: dict[str, Any] | None = None
    while_handling_event: BaseEvent[Any] | None = None

    def __init__(self, message: str, short_term_memory: str | None=None, long_term_memory: str | None=None, details: dict[str, Any] | None=None, event: BaseEvent[Any] | None=None):
        """Initialize a BrowserError with structured memory contexts.

		Args:
			message: Technical error message for logging and debugging
			short_term_memory: Context shown once to LLM (e.g., available actions, options)
			long_term_memory: Persistent error info stored in agent memory
			details: Additional metadata for debugging
			event: The browser event that triggered this error
		"""
        self.message = message
        self.short_term_memory = short_term_memory
        self.long_term_memory = long_term_memory
        self.details = details
        self.while_handling_event = event
        super().__init__(message)

    def __str__(self) -> str:
        if self.details:
            return f'{self.message} ({self.details}) during: {self.while_handling_event}'
        elif self.while_handling_event:
            return f'{self.message} (while handling: {self.while_handling_event})'
        else:
            return self.message