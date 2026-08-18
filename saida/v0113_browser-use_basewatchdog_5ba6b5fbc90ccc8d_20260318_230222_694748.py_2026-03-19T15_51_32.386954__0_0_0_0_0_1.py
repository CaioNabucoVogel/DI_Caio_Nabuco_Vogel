@staticmethod
def attach_handler_to_session(browser_session: 'BrowserSession', event_class: type[BaseEvent[Any]], handler) -> None:
    """Attach a single event handler to a browser session.

		Args:
			browser_session: The browser session to attach to
			event_class: The event class to listen for
			handler: The handler method (must start with 'on_' and end with event type)
		"""
    event_bus = browser_session.event_bus
    assert hasattr(handler, '__name__'), 'Handler must have a __name__ attribute'
    assert handler.__name__.startswith('on_'), f'Handler {handler.__name__} must start with "on_"'
    assert handler.__name__.endswith(event_class.__name__), f'Handler {handler.__name__} must end with event type {event_class.__name__}'
    watchdog_instance = getattr(handler, '__self__', None)
    watchdog_class_name = watchdog_instance.__class__.__name__ if watchdog_instance else 'Unknown'

    def make_unique_handler(actual_handler):

        async def unique_handler(event):
            parent_event = event_bus.event_history.get(event.event_parent_id) if event.event_parent_id else None
            grandparent_event = event_bus.event_history.get(parent_event.event_parent_id) if parent_event and parent_event.event_parent_id else None
            parent = f'↲  triggered by on_{parent_event.event_type}#{parent_event.event_id[-4:]}' if parent_event else '👈 by Agent'
            grandparent = (f'↲  under {grandparent_event.event_type}#{grandparent_event.event_id[-4:]}' if grandparent_event else '👈 by Agent') if parent_event else ''
            event_str = f'#{event.event_id[-4:]}'
            time_start = time.time()
            watchdog_and_handler_str = f'[{watchdog_class_name}.{actual_handler.__name__}({event_str})]'.ljust(54)
            browser_session.logger.debug(f'🚌 {watchdog_and_handler_str} ⏳ Starting...       {parent} {grandparent}')
            try:
                result = await actual_handler(event)
                if isinstance(result, Exception):
                    raise result
                time_end = time.time()
                time_elapsed = time_end - time_start
                result_summary = '' if result is None else f' ➡️ <{type(result).__name__}>'
                parents_summary = f' {parent}'.replace('↲  triggered by ', '⤴  returned to  ').replace('👈 by Agent', '👉 returned to  Agent')
                browser_session.logger.debug(f'🚌 {watchdog_and_handler_str} Succeeded ({time_elapsed:.2f}s){result_summary}{parents_summary}')
                return result
            except Exception as e:
                time_end = time.time()
                time_elapsed = time_end - time_start
                original_error = e
                browser_session.logger.error(f'🚌 {watchdog_and_handler_str} ❌ Failed ({time_elapsed:.2f}s): {type(e).__name__}: {e}')
                try:
                    if browser_session.agent_focus_target_id:
                        target_id_to_restore = browser_session.agent_focus_target_id
                        browser_session.logger.debug(f'🚌 {watchdog_and_handler_str} ⚠️ Session error detected, waiting for CDP events to sync (target: {target_id_to_restore})')
                        await browser_session.get_or_create_cdp_session(target_id=target_id_to_restore, focus=True)
                    else:
                        await browser_session.get_or_create_cdp_session(target_id=None, focus=True)
                except Exception as sub_error:
                    if 'ConnectionClosedError' in str(type(sub_error)) or 'ConnectionError' in str(type(sub_error)):
                        browser_session.logger.error(f'🚌 {watchdog_and_handler_str} ❌ Browser closed or CDP Connection disconnected by remote. {type(sub_error).__name__}: {sub_error}\n')
                        raise
                    else:
                        browser_session.logger.error(f'🚌 {watchdog_and_handler_str} ❌ CDP connected but failed to re-create CDP session after error "{type(original_error).__name__}: {original_error}" in {actual_handler.__name__}({event.event_type}#{event.event_id[-4:]}): due to {type(sub_error).__name__}: {sub_error}\n')
                raise
        return unique_handler
    unique_handler = make_unique_handler(handler)
    unique_handler.__name__ = f'{watchdog_class_name}.{handler.__name__}'
    existing_handlers = event_bus.handlers.get(event_class.__name__, [])
    handler_names = [getattr(h, '__name__', str(h)) for h in existing_handlers]
    if unique_handler.__name__ in handler_names:
        raise RuntimeError(f'[{watchdog_class_name}] Duplicate handler registration attempted! Handler {unique_handler.__name__} is already registered for {event_class.__name__}. This likely means attach_to_session() was called multiple times.')
    event_bus.on(event_class, unique_handler)