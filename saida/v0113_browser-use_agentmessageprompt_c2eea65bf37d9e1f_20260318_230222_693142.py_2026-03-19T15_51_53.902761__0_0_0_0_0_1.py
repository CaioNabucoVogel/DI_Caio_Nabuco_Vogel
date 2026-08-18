def __init__(self, browser_state_summary: 'BrowserStateSummary', file_system: 'FileSystem', agent_history_description: str | None=None, read_state_description: str | None=None, task: str | None=None, include_attributes: list[str] | None=None, step_info: Optional['AgentStepInfo']=None, page_filtered_actions: str | None=None, max_clickable_elements_length: int=40000, sensitive_data: str | None=None, available_file_paths: list[str] | None=None, screenshots: list[str] | None=None, vision_detail_level: Literal['auto', 'low', 'high']='auto', include_recent_events: bool=False, sample_images: list[ContentPartTextParam | ContentPartImageParam] | None=None, read_state_images: list[dict] | None=None, llm_screenshot_size: tuple[int, int] | None=None, unavailable_skills_info: str | None=None):
    self.browser_state: 'BrowserStateSummary' = browser_state_summary
    self.file_system: 'FileSystem | None' = file_system
    self.agent_history_description: str | None = agent_history_description
    self.read_state_description: str | None = read_state_description
    self.task: str | None = task
    self.include_attributes = include_attributes
    self.step_info = step_info
    self.page_filtered_actions: str | None = page_filtered_actions
    self.max_clickable_elements_length: int = max_clickable_elements_length
    self.sensitive_data: str | None = sensitive_data
    self.available_file_paths: list[str] | None = available_file_paths
    self.screenshots = screenshots or []
    self.vision_detail_level = vision_detail_level
    self.include_recent_events = include_recent_events
    self.sample_images = sample_images or []
    self.read_state_images = read_state_images or []
    self.unavailable_skills_info: str | None = unavailable_skills_info
    self.llm_screenshot_size = llm_screenshot_size
    assert self.browser_state