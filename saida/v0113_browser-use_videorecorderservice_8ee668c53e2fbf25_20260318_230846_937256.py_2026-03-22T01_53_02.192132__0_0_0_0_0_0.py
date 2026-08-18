class VideoRecorderService:
    """
	Handles the video encoding process for a browser session using imageio.

	This service captures individual frames from the CDP screencast, decodes them,
	and appends them to a video file using a pip-installable ffmpeg backend.
	It automatically resizes frames to match the target video dimensions.
	"""

    def __init__(self, output_path: Path, size: ViewportSize, framerate: int):
        """
		Initializes the video recorder.

		Args:
		    output_path: The full path where the video will be saved.
		    size: A ViewportSize object specifying the width and height of the video.
		    framerate: The desired framerate for the output video.
		"""
        self.output_path = output_path
        self.size = size
        self.framerate = framerate
        self._writer: Optional['Format.Writer'] = None
        self._is_active = False
        self.padded_size = _get_padded_size(self.size)

    def start(self) -> None:
        """
		Prepares and starts the video writer.

		If the required optional dependencies are not installed, this method will
		log an error and do nothing.
		"""
        if not IMAGEIO_AVAILABLE:
            logger.error('MP4 recording requires optional dependencies. Please install them with: pip install "browser-use[video]"')
            return
        try:
            self.output_path.parent.mkdir(parents=True, exist_ok=True)
            self._writer = iio.get_writer(str(self.output_path), fps=self.framerate, codec='libx264', quality=8, pixelformat='yuv420p', macro_block_size=None)
            self._is_active = True
            logger.debug(f'Video recorder started. Output will be saved to {self.output_path}')
        except Exception as e:
            logger.error(f'Failed to initialize video writer: {e}')
            self._is_active = False

    def add_frame(self, frame_data_b64: str) -> None:
        """
		Decodes a base64-encoded PNG frame, resizes it, pads it to be codec-compatible,
		and appends it to the video.

		Args:
		    frame_data_b64: A base64-encoded string of the PNG frame data.
		"""
        if not self._is_active or not self._writer:
            return
        try:
            frame_bytes = base64.b64decode(frame_data_b64)
            with Image.open(io.BytesIO(frame_bytes)) as img:
                if img.size != (self.size['width'], self.size['height']):
                    img = img.resize((self.size['width'], self.size['height']), Image.Resampling.BICUBIC)
                if self.padded_size['width'] != self.size['width'] or self.padded_size['height'] != self.size['height']:
                    new_img = Image.new('RGB', (self.padded_size['width'], self.padded_size['height']), (0, 0, 0))
                    x_offset = (self.padded_size['width'] - self.size['width']) // 2
                    y_offset = (self.padded_size['height'] - self.size['height']) // 2
                    new_img.paste(img, (x_offset, y_offset))
                    img = new_img
                img_array = np.array(img)
            self._writer.append_data(img_array)
        except Exception as e:
            logger.warning(f'Could not process and add video frame: {e}')

    def stop_and_save(self) -> None:
        """
		Finalizes the video file by closing the writer.

		This method should be called when the recording session is complete.
		"""
        if not self._is_active or not self._writer:
            return
        try:
            self._writer.close()
            logger.info(f'📹 Video recording saved successfully to: {self.output_path}')
        except Exception as e:
            logger.error(f'Failed to finalize and save video: {e}')
        finally:
            self._is_active = False
            self._writer = None