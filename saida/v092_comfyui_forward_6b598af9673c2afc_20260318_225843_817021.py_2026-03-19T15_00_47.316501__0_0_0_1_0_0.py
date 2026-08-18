def forward(self, prompt_embeds, id_embeds, class_tokens_mask) -> torch.Tensor:
    id_embeds = id_embeds.to(prompt_embeds.dtype)
    num_inputs = class_tokens_mask.sum().unsqueeze(0)
    (batch_size, max_num_inputs) = id_embeds.shape[:2]
    seq_length = prompt_embeds.shape[1]
    flat_id_embeds = id_embeds.view(-1, id_embeds.shape[-2], id_embeds.shape[-1])
    valid_id_mask = torch.arange(max_num_inputs, device=flat_id_embeds.device)[None, :] < num_inputs[:, None]
    valid_id_embeds = flat_id_embeds[valid_id_mask.flatten()]
    prompt_embeds = prompt_embeds.view(-1, prompt_embeds.shape[-1])
    class_tokens_mask = class_tokens_mask.view(-1)
    valid_id_embeds = valid_id_embeds.view(-1, valid_id_embeds.shape[-1])
    image_token_embeds = prompt_embeds[class_tokens_mask]
    stacked_id_embeds = self.fuse_fn(image_token_embeds, valid_id_embeds)
    assert class_tokens_mask.sum() == stacked_id_embeds.shape[0], f'{class_tokens_mask.sum()} != {stacked_id_embeds.shape[0]}'
    prompt_embeds.masked_scatter_(class_tokens_mask[:, None], stacked_id_embeds.to(prompt_embeds.dtype))
    updated_prompt_embeds = prompt_embeds.view(batch_size, seq_length, -1)
    return updated_prompt_embeds