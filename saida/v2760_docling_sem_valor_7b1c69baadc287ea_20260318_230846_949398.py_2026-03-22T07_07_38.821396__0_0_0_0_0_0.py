def predict_batch(self, input_batch: List[ObjectDetectionEngineInput]) -> List[ObjectDetectionEngineOutput]:
    """Run inference on a batch of images against a KServe v2 endpoint."""
    if not input_batch:
        return []
    if not self._initialized:
        raise RuntimeError('Engine not initialized. Call initialize() first.')
    assert self._processor is not None
    assert self._kserve_client is not None
    assert self._input_images_name is not None
    assert self._input_orig_target_sizes_name is not None
    assert self._output_labels_name is not None
    assert self._output_boxes_name is not None
    assert self._output_scores_name is not None
    images = [item.image.convert('RGB') for item in input_batch]
    processed_inputs = self._processor(images=images, return_tensors='np')
    pixel_values = np.asarray(processed_inputs['pixel_values'], dtype=np.float32)
    orig_sizes = np.asarray([[image.width, image.height] for image in images], dtype=np.int64)
    outputs = self._kserve_client.infer(inputs={self._input_images_name: pixel_values, self._input_orig_target_sizes_name: orig_sizes}, output_names=[self._output_labels_name, self._output_boxes_name, self._output_scores_name], request_parameters=self.options.request_parameters)
    try:
        labels_batch = outputs[self._output_labels_name]
        boxes_batch = outputs[self._output_boxes_name]
        scores_batch = outputs[self._output_scores_name]
    except KeyError as exc:
        raise RuntimeError(f'Missing one or more expected KServe v2 outputs: {self._output_labels_name}, {self._output_boxes_name}, {self._output_scores_name}') from exc
    if len(labels_batch) != len(input_batch):
        raise RuntimeError(f'KServe v2 output batch size mismatch for labels: expected {len(input_batch)}, got {len(labels_batch)}')
    batch_outputs: List[ObjectDetectionEngineOutput] = []
    for (idx, input_item) in enumerate(input_batch):
        batch_outputs.append(self._build_output(input_item=input_item, labels=labels_batch[idx], scores=scores_batch[idx], boxes=boxes_batch[idx], apply_score_threshold=True))
    return batch_outputs