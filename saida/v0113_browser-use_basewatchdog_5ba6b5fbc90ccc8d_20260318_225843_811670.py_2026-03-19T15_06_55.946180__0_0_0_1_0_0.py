def attach_to_session(self) -> None:
    """Attach watchdog to its browser session and start monitoring.

		This method handles event listener registration. The watchdog is already
		bound to a browser session via self.browser_session from initialization.
		"""
    assert self.browser_session is not None, 'Root CDP client not initialized - browser may not be connected yet'
    from browser_use.browser import events
    event_classes = {}
    for name in dir(events):
        obj = getattr(events, name)
        if inspect.isclass(obj) and issubclass(obj, BaseEvent) and (obj is not BaseEvent):
            event_classes[name] = obj
    registered_events = set()
    for method_name in dir(self):
        if method_name.startswith('on_') and callable(getattr(self, method_name)):
            event_name = method_name[3:]
            if event_name in event_classes:
                event_class = event_classes[event_name]
                if self.LISTENS_TO:
                    assert event_class in self.LISTENS_TO, f'[{self.__class__.__name__}] Handler {method_name} listens to {event_name} but {event_name} is not declared in LISTENS_TO: {[e.__name__ for e in self.LISTENS_TO]}'
                handler = getattr(self, method_name)
                self.attach_handler_to_session(self.browser_session, event_class, handler)
                registered_events.add(event_class)
    if self.LISTENS_TO:
        missing_handlers = set(self.LISTENS_TO) - registered_events
        if missing_handlers:
            missing_names = [e.__name__ for e in missing_handlers]
            self.logger.warning(f"[{self.__class__.__name__}] LISTENS_TO declares {missing_names} but no handlers found (missing on_{'_, on_'.join(missing_names)} methods)")