def optimizer_hook(param):
    if param.grad is not None:
        optimizer_dict[param].step()
        optimizer_dict[param].zero_grad()