from .mino_shape import mino_map
from ..consts.ui_consts import UI_CONSTS


class Mino:
    def __init__(self, shape_index: int):
        self.shape_index: int = shape_index  # mino_map 인덱스
        self.color_index: int = self.shape_index + 1  # t_color 인덱스
        self.color = UI_CONSTS.t_color[self.shape_index + 1]
        self.shape = mino_map[self.shape_index]
