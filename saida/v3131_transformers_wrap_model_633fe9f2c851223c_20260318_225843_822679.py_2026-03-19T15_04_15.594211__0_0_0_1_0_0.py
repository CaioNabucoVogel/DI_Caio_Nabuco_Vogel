def patched_optimizer_step(optimizer, barrier=False, optimizer_args={}):
    loss = optimizer.step(**optimizer_args)
    if barrier:
        xm.mark_step()
    return loss