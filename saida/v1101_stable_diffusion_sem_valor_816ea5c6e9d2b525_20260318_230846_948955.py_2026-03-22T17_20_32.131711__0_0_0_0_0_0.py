def split_cross_attention_forward_invokeAI(self, x, context=None, mask=None, **kwargs):
    h = self.heads
    q = self.to_q(x)
    context = default(context, x)
    (context_k, context_v) = hypernetwork.apply_hypernetworks(shared.loaded_hypernetworks, context)
    k = self.to_k(context_k)
    v = self.to_v(context_v)
    del context, context_k, context_v, x
    dtype = q.dtype
    if shared.opts.upcast_attn:
        (q, k, v) = (q.float(), k.float(), v if v.device.type == 'mps' else v.float())
    with devices.without_autocast(disable=not shared.opts.upcast_attn):
        k = k * self.scale
        (q, k, v) = (rearrange(t, 'b n (h d) -> (b h) n d', h=h) for t in (q, k, v))
        r = einsum_op(q, k, v)
    r = r.to(dtype)
    return self.to_out(rearrange(r, '(b h) n d -> b n (h d)', h=h))