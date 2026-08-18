def draw_star(frame: Image.Image, center: tuple[int, int], size: int, fill_color: tuple[int, int, int], outline_color: Optional[tuple[int, int, int]]=None, outline_width: int=1) -> Image.Image:
    """
    Draw a 5-pointed star.

    Args:
        frame: PIL Image to draw on
        center: (x, y) center position
        size: Star size (outer radius)
        fill_color: RGB fill color
        outline_color: RGB outline color (None for no outline)
        outline_width: Outline width

    Returns:
        Modified frame
    """
    import math
    draw = ImageDraw.Draw(frame)
    (x, y) = center
    points = []
    for i in range(10):
        angle = (i * 36 - 90) * math.pi / 180
        radius = size if i % 2 == 0 else size * 0.4
        px = x + radius * math.cos(angle)
        py = y + radius * math.sin(angle)
        points.append((px, py))
    draw.polygon(points, fill=fill_color, outline=outline_color, width=outline_width)
    return frame