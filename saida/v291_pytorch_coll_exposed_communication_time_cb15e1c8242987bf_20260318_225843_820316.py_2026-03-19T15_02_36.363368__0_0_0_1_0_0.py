def accumulate_time(_snode: BaseSchedulerNode) -> None:
    nonlocal comp_time
    comp_time += runtimes[_snode]