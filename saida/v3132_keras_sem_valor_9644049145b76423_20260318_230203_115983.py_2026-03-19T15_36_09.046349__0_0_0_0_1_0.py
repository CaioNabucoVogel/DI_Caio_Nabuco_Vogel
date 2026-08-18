def _masked_softmax(self, attention_scores, attention_mask=None):
    if attention_mask is not None:
        mask_expansion_axis = -len(self._attention_axes) * 2 - 1
        for _ in range(len(attention_scores.shape) - len(attention_mask.shape)):
            attention_mask = ops.expand_dims(attention_mask, axis=mask_expansion_axis)
    return self._softmax(attention_scores, mask=attention_mask)