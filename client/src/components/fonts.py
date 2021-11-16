from pygame.font import Font
from ..consts.asset_paths import Path
font_path = Path.font_path
font_path_b = Path.font_path_b
font_path_i = Path.font_path_i


class FONTS:
    h1 = Font(font_path, 50)
    h2 = Font(font_path, 30)
    h4 = Font(font_path, 20)
    h5 = Font(font_path, 13)
    h6 = Font(font_path, 10)

    h1_b = Font(font_path_b, 50)
    h2_b = Font(font_path_b, 30)

    h2_i = Font(font_path_i, 30)
    h5_i = Font(font_path_i, 13)
