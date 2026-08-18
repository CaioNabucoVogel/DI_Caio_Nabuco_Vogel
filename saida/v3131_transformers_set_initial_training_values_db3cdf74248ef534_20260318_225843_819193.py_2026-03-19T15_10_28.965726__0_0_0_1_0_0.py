def set_initial_training_values(self, args: TrainingArguments, dataloader: DataLoader, total_train_batch_size: int):
    """
        Calculates and returns the following values:
        - `num_train_epochs`
        - `num_update_steps_per_epoch`
        - `num_examples`
        - `num_train_samples`
        - `epoch_based`
        - `len_dataloader`
        - `max_steps`
        """
    max_steps = args.max_steps
    epoch_based = max_steps < 0
    len_dataloader = len(dataloader) if has_length(dataloader) else None
    sp_size = self.get_sp_size()
    if sp_size > 1 and len_dataloader is not None:
        len_dataloader = len_dataloader * sp_size
    if len_dataloader is not None:
        num_update_steps_per_epoch = max(len_dataloader // args.gradient_accumulation_steps + int(len_dataloader % args.gradient_accumulation_steps > 0), 1)
        if epoch_based:
            max_steps = math.ceil(args.num_train_epochs * num_update_steps_per_epoch)
    if len_dataloader:
        num_examples = self.num_examples(dataloader)
        if args.max_steps > 0:
            num_train_epochs = max_steps // num_update_steps_per_epoch + int(max_steps % num_update_steps_per_epoch > 0)
            num_train_samples = max_steps * total_train_batch_size
        else:
            num_train_epochs = math.ceil(args.num_train_epochs)
            num_train_samples = self.num_examples(dataloader) * args.num_train_epochs
    elif args.max_steps > 0:
        num_train_epochs = sys.maxsize
        num_update_steps_per_epoch = max_steps
        num_examples = total_train_batch_size * args.max_steps
        num_train_samples = args.max_steps * total_train_batch_size
    else:
        raise ValueError(f'args.max_steps must be set to a positive value if dataloader does not have a length, was {args.max_steps}')
    return (num_train_epochs, num_update_steps_per_epoch, num_examples, num_train_samples, epoch_based, len_dataloader, max_steps)