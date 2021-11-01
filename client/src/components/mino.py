from .mino_shape import mino_map
from ..variables.ui_variables import UI_VARIABLES


class Mino:
    def __init__(self, shape_index: int):
        self.shape_index: int = shape_index  # mino_map 인덱스
        self.color_index: int = self.shape_index + 1  # t_color 인덱스
        self.color = UI_VARIABLES.t_color[self.shape_index + 1]
        self.shape = mino_map[self.shape_index]
