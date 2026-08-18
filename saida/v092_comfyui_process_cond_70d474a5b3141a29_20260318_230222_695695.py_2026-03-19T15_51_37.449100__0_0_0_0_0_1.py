def process_cond(self, batch_size, area, **kwargs):
    data = self.cond
    if area is not None:
        dims = len(area) // 2
        for i in range(dims):
            data = data.narrow(i + 2, area[i + dims], area[i])
    return self._copy_with(comfy.utils.repeat_to_batch_size(data, batch_size))