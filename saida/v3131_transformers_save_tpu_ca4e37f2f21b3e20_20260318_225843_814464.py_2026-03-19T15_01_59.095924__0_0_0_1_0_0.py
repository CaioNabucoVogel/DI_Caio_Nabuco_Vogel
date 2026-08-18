def _save_tpu(self, output_dir: str | None=None):
    output_dir = output_dir if output_dir is not None else self.args.output_dir
    logger.info(f'Saving model checkpoint to {output_dir}')
    model = self.model
    xm.mark_step()
    if xm.is_master_ordinal(local=False):
        os.makedirs(output_dir, exist_ok=True)
        torch.save(self.args, os.path.join(output_dir, TRAINING_ARGS_NAME))
    supported_classes = (PushToHubMixin,)
    xm.rendezvous('saving_checkpoint')
    if self.is_fsdp_xla_v1_enabled:
        ckpt = {'model': model.state_dict(), 'shard_metadata': model.get_shard_metadata()}
        ckpt_path = os.path.join(output_dir, f'rank{self.args.process_index}-of-{self.args.world_size}-{WEIGHTS_NAME}')
        xm.save(ckpt, ckpt_path, master_only=False)
        xm.rendezvous('save_full_checkpoints')
        if self.args.should_save:
            from torch_xla.distributed.fsdp import consolidate_sharded_model_checkpoints
            (full_state_dict, _) = consolidate_sharded_model_checkpoints(ckpt_prefix=os.path.join(output_dir, ''), ckpt_suffix=f'rank*-of-*-{WEIGHTS_NAME}', save_model=False)
            model = model.module.module
            unwrapped_model = self.accelerator.unwrap_model(model)
            if isinstance(unwrapped_model, supported_classes):
                unwrapped_model.save_pretrained(output_dir, state_dict=full_state_dict)
            else:
                logger.info('Trainer.model is not a `PreTrainedModel`, only saving its state dict.')
                xm.save(full_state_dict, os.path.join(output_dir, WEIGHTS_NAME))
    elif not isinstance(model, supported_classes):
        if isinstance(self.accelerator.unwrap_model(model), supported_classes):
            self.accelerator.unwrap_model(model).save_pretrained(output_dir, is_main_process=self.args.should_save, state_dict=xm._maybe_convert_to_cpu(model.state_dict()))
        else:
            logger.info('Trainer.model is not a `PreTrainedModel`, only saving its state dict.')
            state_dict = xm._maybe_convert_to_cpu(model.state_dict())
            xm.save(state_dict, os.path.join(output_dir, WEIGHTS_NAME))
    else:
        model.save_pretrained(output_dir, is_main_process=self.args.should_save, state_dict=xm._maybe_convert_to_cpu(model.state_dict()))
    if self.processing_class is not None and self.args.should_save:
        self.processing_class.save_pretrained(output_dir)