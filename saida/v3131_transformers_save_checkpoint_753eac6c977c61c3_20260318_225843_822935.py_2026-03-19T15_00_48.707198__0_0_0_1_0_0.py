def _save_checkpoint(self, model, trial):
    checkpoint_folder = f'{PREFIX_CHECKPOINT_DIR}-{self.state.global_step}'
    if self.hp_search_backend is None and trial is None:
        self.store_flos()
    run_dir = self._get_output_dir(trial=trial)
    output_dir = os.path.join(run_dir, checkpoint_folder)
    self.save_model(output_dir, _internal_call=True)
    if self.args.save_strategy in [SaveStrategy.STEPS, SaveStrategy.EPOCH] and self.state.best_global_step:
        if is_torch_xla_available():
            xm.rendezvous('load_best_model_at_end')
        elif self.args.parallel_mode == ParallelMode.DISTRIBUTED:
            dist.barrier()
        elif is_sagemaker_mp_enabled():
            smp.barrier()
        best_checkpoint_folder = f'{PREFIX_CHECKPOINT_DIR}-{self.state.best_global_step}'
        best_checkpoint_dir = os.path.join(run_dir, best_checkpoint_folder)
        if os.path.exists(best_checkpoint_dir):
            self.state.best_model_checkpoint = best_checkpoint_dir
    if not self.args.save_only_model:
        self._save_optimizer_and_scheduler(output_dir)
        self._save_scaler(output_dir)
        self._save_rng_state(output_dir)
    if self.args.should_save:
        for cb in [cb for cb in self.callback_handler.callbacks + [self.control] if isinstance(cb, ExportableState)]:
            cb_name = cb.__class__.__name__
            cb_state = cb.state()
            if isinstance(self.state.stateful_callbacks[cb_name], list):
                self.state.stateful_callbacks[cb_name].append(cb_state)
            else:
                self.state.stateful_callbacks[cb_name] = cb_state
        self.state.save_to_json(os.path.join(output_dir, TRAINER_STATE_NAME))
    if self.args.push_to_hub:
        self._push_from_checkpoint(output_dir)
    if self.args.should_save:
        self._rotate_checkpoints(use_mtime=True, output_dir=run_dir)