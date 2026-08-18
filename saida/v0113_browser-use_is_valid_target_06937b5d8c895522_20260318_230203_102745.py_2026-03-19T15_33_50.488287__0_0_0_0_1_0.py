def _is_valid_target(target_info: TargetInfo, include_http: bool=True, include_chrome: bool=False, include_chrome_extensions: bool=False, include_chrome_error: bool=False, include_about: bool=True, include_iframes: bool=True, include_pages: bool=True, include_workers: bool=False) -> bool:
    """Check if a target should be processed.

		Args:
			target_info: Target info dict from CDP

		Returns:
			True if target should be processed, False if it should be skipped
		"""
    target_type = target_info.get('type', '')
    url = target_info.get('url', '')
    (url_allowed, type_allowed) = (False, False)
    from browser_use.utils import is_new_tab_page
    if is_new_tab_page(url):
        url_allowed = True
    if url.startswith('chrome-error://') and include_chrome_error:
        url_allowed = True
    if url.startswith('chrome://') and include_chrome:
        url_allowed = True
    if url.startswith('chrome-extension://') and include_chrome_extensions:
        url_allowed = True
    if url == 'about:blank' and include_about:
        url_allowed = True
    if (url.startswith('http://') or url.startswith('https://')) and include_http:
        url_allowed = True
    if target_type in ('service_worker', 'shared_worker', 'worker') and include_workers:
        type_allowed = True
    if target_type in ('page', 'tab') and include_pages:
        type_allowed = True
    if target_type in ('iframe', 'webview') and include_iframes:
        type_allowed = True
    return url_allowed and type_allowed