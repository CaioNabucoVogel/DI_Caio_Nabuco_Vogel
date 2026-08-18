def __call__(self, conv_res: ConversionResult, page_batch: Iterable[Page]) -> Iterable[Page]:
    page_list = list(page_batch)
    if not page_list:
        return
    valid_pages = []
    invalid_pages = []
    for page in page_list:
        assert page._backend is not None
        if not page._backend.is_valid():
            invalid_pages.append(page)
        else:
            valid_pages.append(page)
    if valid_pages:
        with TimeRecorder(conv_res, f'vlm-mlx-{self.vlm_options.repo_id}'):
            images = []
            user_prompts = []
            pages_with_images = []
            for page in valid_pages:
                assert page.size is not None
                hi_res_image = page.get_image(scale=self.vlm_options.scale, max_size=self.vlm_options.max_size)
                if hi_res_image is not None:
                    images.append(hi_res_image)
                    user_prompt = self._build_prompt_safe(page)
                    user_prompts.append(user_prompt)
                    pages_with_images.append(page)
            if images:
                predictions = list(self.process_images(images, user_prompts))
                for (page, prediction) in zip(pages_with_images, predictions):
                    page.predictions.vlm_response = prediction
    for page in invalid_pages:
        yield page
    for page in valid_pages:
        yield page