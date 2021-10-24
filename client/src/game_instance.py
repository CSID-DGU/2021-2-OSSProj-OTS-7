from client.src.components.board import Board
import copy
from random import randint
from client.src.components.mino import Mino


def new_mino():
    return Mino(shape_index=randint(0, 6))


class GameInstance:
    def __init__(self, is_multiplayer=False):
        self.board = Board()  # 테트리스 판

        self.is_multiplayer = is_multiplayer
        # if is_multiplayer:

        self.score = 0
        self.level = 1
        self.goal = self.level * 5
        self.freeze_time_count = 0
        self.is_hard_dropped = False  # 하드드롭 여부

        self.display_update_required = True

        self.x = 3  # current mino 위치
        self.y = 0
        self.rotation = 0
        self.move_down_count = 5  # 레벨 1일때 move down count

        self.current_mino = new_mino()
        self.next_mino = new_mino()

        self.is_hold_used = False  # Hold 여부
        self.hold_mino = None

        self.status = 'start_screen'

    def reset(self):
        self.__init__()

    # 이하 상태
    def is_stackable(self) -> bool:  # 다음 블록을 쌓을 수 있는 상황인지 판별함. 게임 오버 판별기
        grid = self.next_mino.shape[0]

        for i in range(4):
            for j in range(4):
                if grid[i][j] != 0 and self.board.frozen_matrix[3 + j][i] != 0:
                    return False
        return True

    def get_rotation(self, modifier: int) -> int:  # 현재 회전의 index 에 modifier 를 더함. 리스트 범위 넘어가는 것 처리
        temp = self.rotation + modifier

        if temp < 0:
            temp = 3
        elif temp > 3:
            temp = 0

        return temp

    def is_rotatable(self, x, y, r_or_l: str) -> bool:
        mod = 1
        if r_or_l == 'r':
            mod = 1
        elif r_or_l == 'l':
            mod = -1

        grid = self.current_mino.shape[self.get_rotation(mod)]

        for i in range(4):
            for j in range(4):
                if grid[i][j] != 0:
                    if (x + j) < 0 or (x + j) > 9 or (y + i) < 0 or (y + i) > 20:
                        return False
                    elif self.board.frozen_matrix[x + j][y + i] != 0:
                        return False
        return True

    # Returns true if mino is at the left edge
    def is_left_collide(self) -> bool:
        grid = self.current_mino.shape[self.rotation]
        for i in range(4):
            for j in range(4):
                if grid[i][j] != 0:
                    if (self.x + j - 1) < 0:
                        return True
                    elif self.board.frozen_matrix[self.x + j - 1][self.y + i] != 0:
                        return True
        return False

    # Returns true if mino is at the right edge
    def is_right_collide(self) -> bool:
        grid = self.current_mino.shape[self.rotation]
        for i in range(4):
            for j in range(4):
                if grid[i][j] != 0:
                    if (self.x + j + 1) > 9:
                        return True
                    elif self.board.frozen_matrix[self.x + j + 1][self.y + i] != 0:
                        return True
        return False

    def is_bottom_collide(self, x, y) -> bool:
        grid = self.current_mino.shape[self.rotation]
        temp_matrix = copy.deepcopy(self.board.frozen_matrix)

        for i in range(4):
            for j in range(4):
                if grid[i][j] != 0:
                    if (y + i + 1) > 20:
                        return True
                    elif temp_matrix[x + j][y + i + 1] != 0 and temp_matrix[x + j][y + i + 1] != 8:
                        return True
        return False

    ###### move event wrapper ######
    def move(self, func):
        self.board.temp_matrix = copy.deepcopy(self.board.frozen_matrix)
        func()
        self.board.temp_matrix = self.draw_current_mino(self.board.temp_matrix)

    ###### 이벤트 헨들러 ######
    def ev_hard_drop(self):
        self.hard_drop()
        self.is_hard_dropped = True

    def ev_move_down(self):
        if not self.is_bottom_collide(self.x, self.y):
            self.move(self.move_down)
        else:
            self.bottom_count()

    def ev_move_down_manual(self):
        if not self.is_bottom_collide(self.x, self.y):
            self.move(self.move_down)
        else:
            self.freeze_current_mino()

    def ev_move_left(self):
        if not self.is_left_collide():
            self.move(self.move_left)

    def ev_move_right(self):
        if not self.is_right_collide():
            self.move(self.move_right)

    def ev_rotate_right(self):
        mod_list = [0, -1, 1, -2, 2]
        for mod in mod_list:
            if self.is_rotatable(self.x + mod, self.y, 'r'):
                self.rotate(x_mod=mod, right_or_left='r')
                break
            elif self.is_rotatable(self.x, self.y + mod, 'r'):
                self.rotate(y_mod=mod, right_or_left='r')
                break

    def ev_rotate_left(self):
        pass

    def ev_hold_current_mino(self):
        if not self.is_hold_used:
            self.move(self.hold_current_mino)

    def ev_pause_game(self):
        if self.status != 'pause':
            self.status = 'pause'
        elif self.status == 'pause':
            self.status = 'in_game'

    ###### 동작 ######

    def move_down(self):
        self.y += 1
        self.move_down_count = 6 - self.level

    def move_left(self):
        self.x -= 1

    def move_right(self):
        self.x += 1

    def plus_y(self):
        self.y += 1

    def hard_drop(self):
        while not self.is_bottom_collide(self.x, self.y):
            self.move(self.move_down)
        self.freeze_current_mino()

    def hold_current_mino(self):
        self.is_hold_used = True
        if self.hold_mino is None:
            self.hold_mino = self.current_mino
            self.change_to_next_mino()
        else:
            self.freeze_time_count = 0
            self.x, self.y = 3, 0
            self.current_mino, self.hold_mino = self.hold_mino, self.current_mino

    def pause_game(self):
        pass

    def rotate(self, right_or_left='r', x_mod=0, y_mod=0):
        self.x += x_mod
        self.y += y_mod
        if right_or_left == 'r':
            self.rotate_right()
        elif right_or_left == 'l':
            self.rotate_left()
        self.board.temp_matrix = copy.deepcopy(self.board.frozen_matrix)
        self.draw_current_mino(self.board.temp_matrix)

    def rotate_right(self):
        self.rotation = self.get_rotation(1)

    def rotate_left(self):
        self.rotation = self.get_rotation(-1)

    def count_move_down(self):
        self.move_down_count -= 1
        if self.move_down_count < 0:
            self.ev_move_down()
            self.move_down_count = 6 - self.level

    def check_lines(self):  # 라인 제거
        line_count = 0
        for j in range(21):
            is_full = True
            for i in range(10):
                if self.board.temp_matrix[i][j] == 0:
                    is_full = False
            if is_full:
                line_count += 1
                k = j
                while k > 0:
                    for i in range(10):
                        self.board.temp_matrix[i][k] = self.board.temp_matrix[i][k - 1]
                    k -= 1

        score_list = (50, 150, 350, 1000)
        if line_count != 0:
            self.update_score(score_list[line_count - 1] * self.level)
            self.update_goal(line_count)

    def update_score(self, to_add):
        self.score += to_add

    def bottom_count(self):
        if self.is_hard_dropped or self.freeze_time_count == 6:  # 바닥에 닿아도 6틱동안 움직일수 있음
            self.freeze_current_mino()
        else:
            self.freeze_time_count += 1

    def freeze_current_mino(self):
        self.check_lines()
        self.board.frozen_matrix = copy.deepcopy(self.board.temp_matrix)
        self.is_hard_dropped = False
        self.freeze_time_count = 0
        self.update_score(10 * self.level)
        if self.is_stackable():
            self.change_to_next_mino()
            self.rotation = 0
            self.is_hold_used = False
        else:
            self.status = 'game_over'

    def update_goal(self, line_count):
        self.goal -= line_count
        if self.goal < 0:
            self.level += 1
            self.goal += self.level * 5

    def change_to_next_mino(self):
        self.x = 3
        self.y = 0
        self.rotation = 0
        self.freeze_time_count = 0
        self.current_mino = self.next_mino
        self.next_mino = new_mino()
        self.draw_current_mino(self.board.temp_matrix)

    def draw_current_mino(self, matrix):
        grid = self.current_mino.shape[self.rotation]
        tx, ty = self.x, self.y
        while not self.is_bottom_collide(tx, ty):  # ghost
            ty += 1
        for i in range(4):
            for j in range(4):
                if grid[i][j] != 0:
                    # update ghost
                    matrix[tx + j][ty + i] = 8
                    # update current mino
                    matrix[self.x + j][self.y + i] = grid[i][j]
        return matrix

    def on_game_over(self):
        self.reset()
