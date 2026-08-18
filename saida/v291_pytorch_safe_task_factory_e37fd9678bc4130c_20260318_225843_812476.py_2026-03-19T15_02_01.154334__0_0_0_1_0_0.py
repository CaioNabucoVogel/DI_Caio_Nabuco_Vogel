def _safe_task_factory(loop: AbstractEventLoop, coro: TCoro, *, context: Context | None=None) -> asyncio.Future:
    task_factory = task_factories[0]
    if task_factory is None:
        if sys.version_info >= (3, 11):
            task = asyncio.Task(coro, loop=loop, context=context)
        else:
            task = asyncio.Task(coro, loop=loop)
        if task._source_traceback:
            del task._source_traceback[-1]
    elif sys.version_info >= (3, 11):
        task = task_factory(loop, coro, context=context)
    else:
        task = task_factory(loop, coro)
    tasks.add(task)
    return task