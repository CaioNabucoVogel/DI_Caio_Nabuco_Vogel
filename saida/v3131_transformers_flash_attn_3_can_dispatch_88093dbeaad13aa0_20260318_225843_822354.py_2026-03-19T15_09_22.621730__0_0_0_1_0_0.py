def _flash_attn_3_can_dispatch(self, is_init_check: bool=False) -> bool:
    """
        Check the availability of Flash Attention 3 for a given model.

        Args:
            is_init_check (`bool`, *optional*):
                Whether this check is performed early, i.e. at __init__ time, or later when the model and its weights are
                fully instantiated. This is needed as we also check the devices of the weights, which are only available
                later after __init__. This allows to raise proper exceptions early before instantiating the full models
                if we know that the model does not support the requested attention.
        """
    dtype = self.config.dtype
    if not self._supports_flash_attn:
        raise ValueError(f'{self.__class__.__name__} does not support Flash Attention 3 yet. Please request to add support where the model is hosted, on its model hub page: https://huggingface.co/{self.config._name_or_path}/discussions/new or in the Transformers GitHub repo: https://github.com/huggingface/transformers/issues/new')
    if not is_flash_attn_3_available():
        preface = 'FlashAttention3 has been toggled on, but it cannot be used due to the following error:'
        if importlib.util.find_spec('flash_attn_3') is None:
            raise ImportError(f'{preface} the package flash_attn_3 seems to be not installed.')
        if torch.cuda.is_available():
            (major, _) = torch.cuda.get_device_capability()
            if major < 9:
                raise ValueError(f'{preface} Flash Attention 3 requires compute capability >= 9.0, but found {torch.cuda.get_device_capability()} with compute capability {major}.0.')
            else:
                raise ImportError(f'{preface} Flash Attention 3 is not available.')
        else:
            raise ValueError(f'{preface} Flash Attention 3 is not available on CPU. Please make sure torch can access a CUDA device.')
    if dtype is None:
        logger.warning_once('You are attempting to use Flash Attention 3 without specifying a torch dtype. This might lead to unexpected behaviour')
    elif dtype is not None and dtype not in [torch.float16, torch.bfloat16]:
        logger.warning_once(f"""Flash Attention 3 only supports torch.float16 and torch.bfloat16 dtypes, but the current dype in {self.__class__.__name__} is {dtype}. You should run training or inference using Automatic Mixed-Precision via the `with torch.autocast(device_type='torch_device'):` decorator, or load the model with the `dtype` argument. Example: `model = AutoModel.from_pretrained("meta-llama/Llama-3.2-1B", attn_implementation="flash_attention_3", dtype=torch.float16)`""")
    if getattr(self.config, 'alibi', False) or getattr(self.config, 'use_alibi', False):
        raise ValueError('Model is configured to use ALiBi, which is not supported by Flash Attention 3.')
    if hasattr(self.config, 'attention_dropout') and self.config.attention_dropout > 0:
        raise ValueError(f'Model has attention_dropout={self.config.attention_dropout}, which is not supported by Flash Attention 3.')
    if not is_init_check:
        param_devices = list({param.device for param in self.parameters()})
        if len(param_devices) == 1 and param_devices[0].type == 'cpu':
            if torch.cuda.is_available():
                logger.warning_once("You are attempting to use Flash Attention 3 with a model not initialized on GPU. Make sure to move the model to GPU after initializing it on CPU with `model.to('cuda')`.")
            else:
                raise ValueError('You are attempting to use Flash Attention 3 with a model not initialized on GPU and with no GPU available. This is not supported yet. Please make sure to have access to a GPU and either initialise the model on a GPU by passing a device_map or initialising the model on CPU and then moving it to GPU.')
    return True