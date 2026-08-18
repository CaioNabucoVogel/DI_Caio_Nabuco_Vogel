def process_images(self, image_batch: Iterable[Union[Image, np.ndarray]], prompt: Union[str, list[str]]) -> Iterable[VlmPrediction]:
    """Process raw images without page metadata.

        Args:
            image_batch: Iterable of PIL Images or numpy arrays
            prompt: Either:
                - str: Single prompt used for all images
                - list[str]: List of prompts (one per image, must match image count)

        Raises:
            ValueError: If prompt list length doesn't match image count.
        """
    image_list = list(image_batch)
    if len(image_list) == 0:
        return
    if isinstance(prompt, str):
        user_prompts = [prompt] * len(image_list)
    elif isinstance(prompt, list):
        if len(prompt) != len(image_list):
            raise ValueError(f'Number of prompts ({len(prompt)}) must match number of images ({len(image_list)})')
        user_prompts = prompt
    else:
        raise ValueError(f'prompt must be str or list[str], got {type(prompt)}')
    with _MLX_GLOBAL_LOCK:
        _log.debug('MLX model: Acquired global lock for thread safety')
        for (image, user_prompt) in zip(image_list, user_prompts):
            if isinstance(image, np.ndarray):
                if image.ndim == 3 and image.shape[2] in [3, 4]:
                    from PIL import Image as PILImage
                    image = PILImage.fromarray(image.astype(np.uint8))
                elif image.ndim == 2:
                    from PIL import Image as PILImage
                    image = PILImage.fromarray(image.astype(np.uint8), mode='L')
                else:
                    raise ValueError(f'Unsupported numpy array shape: {image.shape}')
            if image.mode != 'RGB':
                image = image.convert('RGB')
            formatted_prompt = self.apply_chat_template(self.processor, self.config, user_prompt, num_images=1)
            start_time = time.time()
            _log.debug('start generating ...')
            tokens: list[VlmPredictionToken] = []
            output = ''
            for token in self.stream_generate(self.vlm_model, self.processor, formatted_prompt, [image], max_tokens=self.max_tokens, verbose=False, temp=self.temperature):
                if len(token.logprobs.shape) == 1:
                    tokens.append(VlmPredictionToken(text=token.text, token=token.token, logprob=token.logprobs[token.token]))
                elif len(token.logprobs.shape) == 2 and token.logprobs.shape[0] == 1:
                    tokens.append(VlmPredictionToken(text=token.text, token=token.token, logprob=token.logprobs[0, token.token]))
                else:
                    _log.warning(f'incompatible shape for logprobs: {token.logprobs.shape}')
                output += token.text
                if self.vlm_options.stop_strings:
                    if any((stop_str in output for stop_str in self.vlm_options.stop_strings)):
                        _log.debug('Stopping generation due to stop string match')
                        break
                if self.vlm_options.custom_stopping_criteria:
                    for criteria in self.vlm_options.custom_stopping_criteria:
                        if isinstance(criteria, GenerationStopper):
                            stopper = criteria
                        elif isinstance(criteria, type) and issubclass(criteria, GenerationStopper):
                            stopper = criteria()
                        lookback_tokens = stopper.lookback_tokens()
                        text_to_check = output[-lookback_tokens:] if len(output) > lookback_tokens else output
                        try:
                            if stopper.should_stop(text_to_check):
                                _log.info(f'Stopping generation due to GenerationStopper: {type(stopper).__name__}')
                                break
                        except Exception as e:
                            _log.warning(f'Error in GenerationStopper.should_stop: {e}')
                            continue
                    else:
                        continue
                    break
            generation_time = time.time() - start_time
            _log.debug(f'{generation_time:.2f} seconds for {len(tokens)} tokens ({len(tokens) / generation_time:.1f} tokens/sec).')
            decoded_output = self.vlm_options.decode_response(output)
            input_prompt = formatted_prompt if self.vlm_options.track_input_prompt else None
            yield VlmPrediction(text=decoded_output, generation_time=generation_time, generated_tokens=tokens, num_tokens=len(tokens), stop_reason=VlmStopReason.UNSPECIFIED, input_prompt=input_prompt)
        _log.debug('MLX model: Released global lock')