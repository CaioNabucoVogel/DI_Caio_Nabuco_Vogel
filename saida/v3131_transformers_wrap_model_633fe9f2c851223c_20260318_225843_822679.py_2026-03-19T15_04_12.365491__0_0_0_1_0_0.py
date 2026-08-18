def shard_output(output, mesh):
    from .modeling_outputs import CausalLMOutputWithPast
    real_output = None
    if isinstance(output, torch.Tensor):
        real_output = output
    elif isinstance(output, tuple):
        real_output = output[0]
    elif isinstance(output, CausalLMOutputWithPast):
        real_output = output.logits
    if real_output is None:
        raise ValueError("Something went wrong, the output of the model shouldn't be `None`")
    xs.mark_sharding(real_output, mesh, ('fsdp', None, None))