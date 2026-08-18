def predict(self, test_dataset: Dataset, ignore_keys: list[str] | None=None, metric_key_prefix: str='test') -> PredictionOutput:
    """
        Run prediction and returns predictions and potential metrics.

        Depending on the dataset and your use case, your test dataset may contain labels. In that case, this method
        will also return metrics, like in `evaluate()`.

        Args:
            test_dataset (`Dataset`):
                Dataset to run the predictions on. If it is an `datasets.Dataset`, columns not accepted by the
                `model.forward()` method are automatically removed. Has to implement the method `__len__`
            ignore_keys (`list[str]`, *optional*):
                A list of keys in the output of your model (if it is a dictionary) that should be ignored when
                gathering predictions.
            metric_key_prefix (`str`, *optional*, defaults to `"test"`):
                An optional prefix to be used as the metrics key prefix. For example the metrics "bleu" will be named
                "test_bleu" if the prefix is "test" (default)

        <Tip>

        If your predictions or labels have different sequence length (for instance because you're doing dynamic padding
        in a token classification task) the predictions will be padded (on the right) to allow for concatenation into
        one array. The padding index is -100.

        </Tip>

        Returns: *NamedTuple* A namedtuple with the following keys:

            - predictions (`np.ndarray`): The predictions on `test_dataset`.
            - label_ids (`np.ndarray`, *optional*): The labels (if the dataset contained some).
            - metrics (`dict[str, float]`, *optional*): The potential dictionary of metrics (if the dataset contained
              labels).
        """
    self._memory_tracker.start()
    test_dataloader = self.get_test_dataloader(test_dataset)
    start_time = time.time()
    output = self.evaluation_loop(test_dataloader, description='Prediction', ignore_keys=ignore_keys, metric_key_prefix=metric_key_prefix)
    total_batch_size = self.args.eval_batch_size * self.args.world_size
    if f'{metric_key_prefix}_model_preparation_time' in output.metrics:
        start_time += output.metrics[f'{metric_key_prefix}_model_preparation_time']
    output.metrics.update(speed_metrics(metric_key_prefix, start_time, num_samples=output.num_samples, num_steps=math.ceil(output.num_samples / total_batch_size)))
    self.control = self.callback_handler.on_predict(self.args, self.state, self.control, output.metrics)
    self._memory_tracker.stop_and_update_metrics(output.metrics)
    return PredictionOutput(predictions=output.predictions, label_ids=output.label_ids, metrics=output.metrics)