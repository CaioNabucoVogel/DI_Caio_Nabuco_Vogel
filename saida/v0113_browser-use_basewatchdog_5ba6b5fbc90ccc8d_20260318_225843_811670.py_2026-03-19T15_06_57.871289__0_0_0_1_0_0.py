def __del__(self) -> None:
    """Clean up any running tasks during garbage collection."""
    try:
        for attr_name in dir(self):
            if attr_name.startswith('_') and attr_name.endswith('_task'):
                try:
                    task = getattr(self, attr_name)
                    if hasattr(task, 'cancel') and callable(task.cancel) and (not task.done()):
                        task.cancel()
                except Exception:
                    pass
            if attr_name.startswith('_') and attr_name.endswith('_tasks') and isinstance(getattr(self, attr_name), Iterable):
                for task in getattr(self, attr_name):
                    try:
                        if hasattr(task, 'cancel') and callable(task.cancel) and (not task.done()):
                            task.cancel()
                    except Exception:
                        pass
    except Exception as e:
        from browser_use.utils import logger
        logger.error(f'⚠️ Error during BrowserSession {self.__class__.__name__} garbage collection __del__(): {type(e)}: {e}')