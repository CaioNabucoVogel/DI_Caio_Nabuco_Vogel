def _calculate_potential_peak_memory_sink_waits(candidate: BaseSchedulerNode, gns: list[BaseSchedulerNode], group_head: BaseSchedulerNode, group_peak_memory: int, candidate_delta_mem: int, candidate_allocfree: SNodeMemory, group_n_to_bufs_after_swap_dealloc_instead_of_candidate: dict, curr_memory: dict, snodes_allocfree: dict) -> tuple[int, dict[BaseSchedulerNode, int], dict[BaseSchedulerNode, int]]:
    """
    Calculate potential peak memory after swapping candidate with group (sink_waits version).

    Computes new memory levels for all affected nodes and returns the potential
    peak memory along with cached post-allocation and size-free delta values.

    Args:
        candidate: Node being moved
        gns: Group nodes
        group_head: First node of group
        group_peak_memory: Current peak memory within the group
        candidate_delta_mem: Net memory change from candidate (alloc - free)
        candidate_allocfree: Candidate's allocation/free info
        group_n_to_bufs_after_swap_dealloc_instead_of_candidate: Buffers whose deallocation moves from candidate to group
        curr_memory: Current memory state dict
        snodes_allocfree: Allocation/free info for all nodes

    Returns:
        Tuple of (potential_peak_memory, post_alloc_update_dict, size_free_delta_update_dict)
    """
    pre_group_mem = curr_memory[group_head][0] - snodes_allocfree[group_head].size_alloc
    _post_alloc_update: dict[BaseSchedulerNode, int] = {}
    _size_free_delta_update: dict[BaseSchedulerNode, int] = {}
    potential_peak = 0
    if not group_n_to_bufs_after_swap_dealloc_instead_of_candidate:
        potential_peak = max(group_peak_memory + candidate_delta_mem, pre_group_mem + candidate_allocfree.size_alloc)
        return (potential_peak, _post_alloc_update, _size_free_delta_update)
    candidate_post_alloc = pre_group_mem + candidate_allocfree.size_alloc
    _post_alloc_update[candidate] = candidate_post_alloc
    potential_peak = candidate_post_alloc
    candidate_size_free_to_move = sum((buf.mpi_buffer.size_free for buf in itertools.chain.from_iterable(group_n_to_bufs_after_swap_dealloc_instead_of_candidate.values())))
    _size_free_delta_update[candidate] = -candidate_size_free_to_move
    delta_mem = candidate_delta_mem + candidate_size_free_to_move
    for gn in gns:
        gn_post_alloc = curr_memory[gn][0] + delta_mem
        _post_alloc_update[gn] = gn_post_alloc
        potential_peak = max(potential_peak, gn_post_alloc)
        gn_size_free_to_add = 0
        if gn in group_n_to_bufs_after_swap_dealloc_instead_of_candidate:
            bufs = group_n_to_bufs_after_swap_dealloc_instead_of_candidate[gn]
            for buf in bufs:
                gn_size_free_to_add += buf.mpi_buffer.size_free
            _size_free_delta_update[gn] = gn_size_free_to_add
        delta_mem -= gn_size_free_to_add
    return (potential_peak, _post_alloc_update, _size_free_delta_update)