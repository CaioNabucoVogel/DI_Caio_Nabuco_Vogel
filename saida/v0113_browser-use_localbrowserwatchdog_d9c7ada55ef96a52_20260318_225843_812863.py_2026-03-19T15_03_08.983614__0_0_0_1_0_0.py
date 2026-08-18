@staticmethod
def _find_installed_browser_path() -> str | None:
    """Try to find browser executable from common fallback locations.

		Prioritizes:
		1. System Chrome Stable
		1. Playwright chromium
		2. Other system native browsers (Chromium -> Chrome Canary/Dev -> Brave)
		3. Playwright headless-shell fallback

		Returns:
			Path to browser executable or None if not found
		"""
    import glob
    import platform
    from pathlib import Path
    system = platform.system()
    patterns = []
    playwright_path = os.environ.get('PLAYWRIGHT_BROWSERS_PATH')
    if system == 'Darwin':
        if not playwright_path:
            playwright_path = '~/Library/Caches/ms-playwright'
        patterns = ['/Applications/Google Chrome.app/Contents/MacOS/Google Chrome', f'{playwright_path}/chromium-*/chrome-mac/Chromium.app/Contents/MacOS/Chromium', '/Applications/Chromium.app/Contents/MacOS/Chromium', '/Applications/Google Chrome Canary.app/Contents/MacOS/Google Chrome Canary', '/Applications/Brave Browser.app/Contents/MacOS/Brave Browser', f'{playwright_path}/chromium_headless_shell-*/chrome-mac/Chromium.app/Contents/MacOS/Chromium']
    elif system == 'Linux':
        if not playwright_path:
            playwright_path = '~/.cache/ms-playwright'
        patterns = ['/usr/bin/google-chrome-stable', '/usr/bin/google-chrome', '/usr/local/bin/google-chrome', f'{playwright_path}/chromium-*/chrome-linux*/chrome', '/usr/bin/chromium', '/usr/bin/chromium-browser', '/usr/local/bin/chromium', '/snap/bin/chromium', '/usr/bin/google-chrome-beta', '/usr/bin/google-chrome-dev', '/usr/bin/brave-browser', f'{playwright_path}/chromium_headless_shell-*/chrome-linux*/chrome']
    elif system == 'Windows':
        if not playwright_path:
            playwright_path = '%LOCALAPPDATA%\\ms-playwright'
        patterns = ['C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe', 'C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe', '%LOCALAPPDATA%\\Google\\Chrome\\Application\\chrome.exe', '%PROGRAMFILES%\\Google\\Chrome\\Application\\chrome.exe', '%PROGRAMFILES(X86)%\\Google\\Chrome\\Application\\chrome.exe', f'{playwright_path}\\chromium-*\\chrome-win\\chrome.exe', 'C:\\Program Files\\Chromium\\Application\\chrome.exe', 'C:\\Program Files (x86)\\Chromium\\Application\\chrome.exe', '%LOCALAPPDATA%\\Chromium\\Application\\chrome.exe', 'C:\\Program Files\\BraveSoftware\\Brave-Browser\\Application\\brave.exe', 'C:\\Program Files (x86)\\BraveSoftware\\Brave-Browser\\Application\\brave.exe', 'C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe', 'C:\\Program Files\\Microsoft\\Edge\\Application\\msedge.exe', '%LOCALAPPDATA%\\Microsoft\\Edge\\Application\\msedge.exe', f'{playwright_path}\\chromium_headless_shell-*\\chrome-win\\chrome.exe']
    for pattern in patterns:
        expanded_pattern = Path(pattern).expanduser()
        if system == 'Windows':
            pattern_str = str(expanded_pattern)
            for env_var in ['%LOCALAPPDATA%', '%PROGRAMFILES%', '%PROGRAMFILES(X86)%']:
                if env_var in pattern_str:
                    env_key = env_var.strip('%').replace('(X86)', ' (x86)')
                    env_value = os.environ.get(env_key, '')
                    if env_value:
                        pattern_str = pattern_str.replace(env_var, env_value)
            expanded_pattern = Path(pattern_str)
        pattern_str = str(expanded_pattern)
        if '*' in pattern_str:
            matches = glob.glob(pattern_str)
            if matches:
                matches.sort()
                browser_path = matches[-1]
                if Path(browser_path).exists() and Path(browser_path).is_file():
                    return browser_path
        elif expanded_pattern.exists() and expanded_pattern.is_file():
            return str(expanded_pattern)
    return None