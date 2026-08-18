class AgentMessagePrompt:
    vision_detail_level: Literal['auto', 'low', 'high']

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

    def _extract_page_statistics(self) -> dict[str, int]:
        """Extract high-level page statistics from DOM tree for LLM context"""
        stats = {'links': 0, 'iframes': 0, 'shadow_open': 0, 'shadow_closed': 0, 'scroll_containers': 0, 'images': 0, 'interactive_elements': 0, 'total_elements': 0}
        if not self.browser_state.dom_state or not self.browser_state.dom_state._root:
            return stats

        def traverse_node(node: SimplifiedNode) -> None:
            """Recursively traverse simplified DOM tree to count elements"""
            if not node or not node.original_node:
                return
            original = node.original_node
            stats['total_elements'] += 1
            if original.node_type == NodeType.ELEMENT_NODE:
                tag = original.tag_name.lower() if original.tag_name else ''
                if tag == 'a':
                    stats['links'] += 1
                elif tag in ('iframe', 'frame'):
                    stats['iframes'] += 1
                elif tag == 'img':
                    stats['images'] += 1
                if original.is_actually_scrollable:
                    stats['scroll_containers'] += 1
                if node.is_interactive:
                    stats['interactive_elements'] += 1
                if node.is_shadow_host:
                    has_closed_shadow = any((child.original_node.node_type == NodeType.DOCUMENT_FRAGMENT_NODE and child.original_node.shadow_root_type and (child.original_node.shadow_root_type.lower() == 'closed') for child in node.children))
                    if has_closed_shadow:
                        stats['shadow_closed'] += 1
                    else:
                        stats['shadow_open'] += 1
            elif original.node_type == NodeType.DOCUMENT_FRAGMENT_NODE:
                pass
            for child in node.children:
                traverse_node(child)
        traverse_node(self.browser_state.dom_state._root)
        return stats

    @observe_debug(ignore_input=True, ignore_output=True, name='_get_browser_state_description')
    def _get_browser_state_description(self) -> str:
        page_stats = self._extract_page_statistics()
        stats_text = '<page_stats>'
        if page_stats['total_elements'] < 10:
            stats_text += 'Page appears empty (SPA not loaded?) - '
        stats_text += f"{page_stats['links']} links, {page_stats['interactive_elements']} interactive, "
        stats_text += f"{page_stats['iframes']} iframes"
        if page_stats['shadow_open'] > 0 or page_stats['shadow_closed'] > 0:
            stats_text += f", {page_stats['shadow_open']} shadow(open), {page_stats['shadow_closed']} shadow(closed)"
        if page_stats['images'] > 0:
            stats_text += f", {page_stats['images']} images"
        stats_text += f", {page_stats['total_elements']} total elements"
        stats_text += '</page_stats>\n'
        elements_text = self.browser_state.dom_state.llm_representation(include_attributes=self.include_attributes)
        if len(elements_text) > self.max_clickable_elements_length:
            elements_text = elements_text[:self.max_clickable_elements_length]
            truncated_text = f' (truncated to {self.max_clickable_elements_length} characters)'
        else:
            truncated_text = ''
        has_content_above = False
        has_content_below = False
        page_info_text = ''
        if self.browser_state.page_info:
            pi = self.browser_state.page_info
            pages_above = pi.pixels_above / pi.viewport_height if pi.viewport_height > 0 else 0
            pages_below = pi.pixels_below / pi.viewport_height if pi.viewport_height > 0 else 0
            has_content_above = pages_above > 0
            has_content_below = pages_below > 0
            total_pages = pi.page_height / pi.viewport_height if pi.viewport_height > 0 else 0
            current_page_position = pi.scroll_y / max(pi.page_height - pi.viewport_height, 1)
            page_info_text = '<page_info>'
            page_info_text += f'{pages_above:.1f} above, '
            page_info_text += f'{pages_below:.1f} below '
            page_info_text += '</page_info>\n'
        if elements_text != '':
            if not has_content_above:
                elements_text = f'[Start of page]\n{elements_text}'
            if not has_content_below:
                elements_text = f'{elements_text}\n[End of page]'
        else:
            elements_text = 'empty page'
        tabs_text = ''
        current_tab_candidates = []
        for tab in self.browser_state.tabs:
            if tab.url == self.browser_state.url and tab.title == self.browser_state.title:
                current_tab_candidates.append(tab.target_id)
        current_target_id = current_tab_candidates[0] if len(current_tab_candidates) == 1 else None
        for tab in self.browser_state.tabs:
            tabs_text += f'Tab {tab.target_id[-4:]}: {tab.url} - {tab.title[:30]}\n'
        current_tab_text = f'Current tab: {current_target_id[-4:]}' if current_target_id is not None else ''
        pdf_message = ''
        if self.browser_state.is_pdf_viewer:
            pdf_message = 'PDF viewer cannot be rendered. In this page, DO NOT use the extract action as PDF content cannot be rendered. '
            pdf_message += 'Use the read_file action on the downloaded PDF in available_file_paths to read the full text content.\n\n'
        recent_events_text = ''
        if self.include_recent_events and self.browser_state.recent_events:
            recent_events_text = f'Recent browser events: {self.browser_state.recent_events}\n'
        closed_popups_text = ''
        if self.browser_state.closed_popup_messages:
            closed_popups_text = 'Auto-closed JavaScript dialogs:\n'
            for popup_msg in self.browser_state.closed_popup_messages:
                closed_popups_text += f'  - {popup_msg}\n'
            closed_popups_text += '\n'
        browser_state = f'{stats_text}{current_tab_text}\nAvailable tabs:\n{tabs_text}\n{page_info_text}\n{recent_events_text}{closed_popups_text}{pdf_message}Interactive elements{truncated_text}:\n{elements_text}\n'
        return browser_state

    def _get_agent_state_description(self) -> str:
        if self.step_info:
            step_info_description = f'Step{self.step_info.step_number + 1} maximum:{self.step_info.max_steps}\n'
        else:
            step_info_description = ''
        time_str = datetime.now().strftime('%Y-%m-%d')
        step_info_description += f'Today:{time_str}'
        _todo_contents = self.file_system.get_todo_contents() if self.file_system else ''
        if not len(_todo_contents):
            _todo_contents = '[empty todo.md, fill it when applicable]'
        agent_state = f"\n<user_request>\n{self.task}\n</user_request>\n<file_system>\n{(self.file_system.describe() if self.file_system else 'No file system available')}\n</file_system>\n<todo_contents>\n{_todo_contents}\n</todo_contents>\n"
        if self.sensitive_data:
            agent_state += f'<sensitive_data>{self.sensitive_data}</sensitive_data>\n'
        agent_state += f'<step_info>{step_info_description}</step_info>\n'
        if self.available_file_paths:
            available_file_paths_text = '\n'.join(self.available_file_paths)
            agent_state += f'<available_file_paths>{available_file_paths_text}\nUse with absolute paths</available_file_paths>\n'
        return agent_state

    def _resize_screenshot(self, screenshot_b64: str) -> str:
        """Resize screenshot to llm_screenshot_size if configured."""
        if not self.llm_screenshot_size:
            return screenshot_b64
        try:
            import base64
            import logging
            from io import BytesIO
            from PIL import Image
            img = Image.open(BytesIO(base64.b64decode(screenshot_b64)))
            if img.size == self.llm_screenshot_size:
                return screenshot_b64
            logging.getLogger(__name__).info(f'🔄 Resizing screenshot from {img.size[0]}x{img.size[1]} to {self.llm_screenshot_size[0]}x{self.llm_screenshot_size[1]} for LLM')
            img_resized = img.resize(self.llm_screenshot_size, Image.Resampling.LANCZOS)
            buffer = BytesIO()
            img_resized.save(buffer, format='PNG')
            return base64.b64encode(buffer.getvalue()).decode('utf-8')
        except Exception as e:
            logging.getLogger(__name__).warning(f'Failed to resize screenshot: {e}, using original')
            return screenshot_b64

    @observe_debug(ignore_input=True, ignore_output=True, name='get_user_message')
    def get_user_message(self, use_vision: bool=True) -> UserMessage:
        """Get complete state as a single cached message"""
        if is_new_tab_page(self.browser_state.url) and self.step_info is not None and (self.step_info.step_number == 0) and (len(self.browser_state.tabs) == 1):
            use_vision = False
        state_description = '<agent_history>\n' + (self.agent_history_description.strip('\n') if self.agent_history_description else '') + '\n</agent_history>\n\n'
        state_description += '<agent_state>\n' + self._get_agent_state_description().strip('\n') + '\n</agent_state>\n'
        state_description += '<browser_state>\n' + self._get_browser_state_description().strip('\n') + '\n</browser_state>\n'
        read_state_description = self.read_state_description.strip('\n').strip() if self.read_state_description else ''
        if read_state_description:
            state_description += '<read_state>\n' + read_state_description + '\n</read_state>\n'
        if self.page_filtered_actions:
            state_description += '<page_specific_actions>\n'
            state_description += self.page_filtered_actions + '\n'
            state_description += '</page_specific_actions>\n'
        if self.unavailable_skills_info:
            state_description += '\n' + self.unavailable_skills_info + '\n'
        state_description = sanitize_surrogates(state_description)
        has_images = bool(self.read_state_images)
        if use_vision is True and self.screenshots or has_images:
            content_parts: list[ContentPartTextParam | ContentPartImageParam] = [ContentPartTextParam(text=state_description)]
            content_parts.extend(self.sample_images)
            for (i, screenshot) in enumerate(self.screenshots):
                if i == len(self.screenshots) - 1:
                    label = 'Current screenshot:'
                else:
                    label = 'Previous screenshot:'
                content_parts.append(ContentPartTextParam(text=label))
                processed_screenshot = self._resize_screenshot(screenshot)
                content_parts.append(ContentPartImageParam(image_url=ImageURL(url=f'data:image/png;base64,{processed_screenshot}', media_type='image/png', detail=self.vision_detail_level)))
            for img_data in self.read_state_images:
                img_name = img_data.get('name', 'unknown')
                img_base64 = img_data.get('data', '')
                if not img_base64:
                    continue
                if img_name.lower().endswith('.png'):
                    media_type = 'image/png'
                else:
                    media_type = 'image/jpeg'
                content_parts.append(ContentPartTextParam(text=f'Image from file: {img_name}'))
                content_parts.append(ContentPartImageParam(image_url=ImageURL(url=f'data:{media_type};base64,{img_base64}', media_type=media_type, detail=self.vision_detail_level)))
            return UserMessage(content=content_parts, cache=True)
        return UserMessage(content=state_description, cache=True)