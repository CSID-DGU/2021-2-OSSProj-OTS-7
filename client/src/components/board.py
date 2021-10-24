import copy

from client.src.variables.ui_variables import UI_VARIABLES as uv

matrix = [[0 for y in range(uv.height + 1)] for x in range(uv.width)]  # Board matrix


class Board:
    def __init__(self):
        self.temp_matrix = copy.deepcopy(matrix)  # 화면 출력용
        self.frozen_matrix = copy.deepcopy(matrix)  # 충돌 계산용
