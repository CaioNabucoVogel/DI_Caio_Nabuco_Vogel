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