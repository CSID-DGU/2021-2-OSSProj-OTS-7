from client.src.components.mino_shape import mino_map
from client.src.variables.ui_variables import UI_VARIABLES


class Mino:
    def __init__(self, shape_index: int):
        self.shape_index = shape_index
        self.color_index = self.shape_index + 1
        self.color = UI_VARIABLES.t_color[self.shape_index + 1]
        self.shape = mino_map[self.shape_index]
