def get_effective_guarantee_steps(self, max_sigma: torch.Tensor):
    """If keyframe starts before current sampling range (max_sigma), treat as 0."""
    if self.start_t > max_sigma:
        return 0
    return self.guarantee_steps