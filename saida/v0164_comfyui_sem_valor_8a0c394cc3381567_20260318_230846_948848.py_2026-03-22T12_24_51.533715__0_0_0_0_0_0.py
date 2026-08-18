def validate_images_aspect_ratio_closeness(first_image: torch.Tensor, second_image: torch.Tensor, min_rel: float, max_rel: float, *, strict: bool=False) -> float:
    """
    Validates that the two images' aspect ratios are 'close'.
    The closeness factor is C = max(ar1, ar2) / min(ar1, ar2)  (C >= 1).
    We require C <= limit, where limit = max(max_rel, 1.0 / min_rel).

    Returns the computed closeness factor C.
    """
    (w1, h1) = get_image_dimensions(first_image)
    (w2, h2) = get_image_dimensions(second_image)
    if min(w1, h1, w2, h2) <= 0:
        raise ValueError('Invalid image dimensions')
    ar1 = w1 / h1
    ar2 = w2 / h2
    closeness = max(ar1, ar2) / min(ar1, ar2)
    limit = max(max_rel, 1.0 / min_rel)
    if closeness >= limit if strict else closeness > limit:
        raise ValueError(f'Aspect ratios must be close: ar1/ar2={ar1 / ar2:.2g}, allowed range {min_rel}–{max_rel} (limit {limit:.2g}).')
    return closeness