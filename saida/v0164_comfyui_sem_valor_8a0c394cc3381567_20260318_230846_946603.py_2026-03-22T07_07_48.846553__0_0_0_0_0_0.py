def load_checkpoint_guess_config_model_only(ckpt_path, embedding_directory=None, model_options={}, te_model_options={}, disable_dynamic=False):
    (model, *_) = load_checkpoint_guess_config(ckpt_path, False, False, False, embedding_directory=embedding_directory, model_options=model_options, te_model_options=te_model_options, disable_dynamic=disable_dynamic)
    return model