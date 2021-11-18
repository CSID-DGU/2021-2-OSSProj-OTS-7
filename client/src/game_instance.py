import pygame
from collections import deque
from .components.board import Board
import copy
from random import randint, choice
from .components.mino import Mino
from .consts.custom_events import custom_events
from .consts import timer_consts as tv


def new_mino():
    return Mino(shape_index=randint(0, 6))


def post_event(custom_event):  # variables/custom_events 참조
    pygame.event.post(pygame.event.Event(custom_events[custom_event]))
    pass


class GameInstance:
    def __init__(self, is_multiplayer=False):
        self.board = Board()  # 테트리스 판

        self.is_multiplayer = is_multiplayer  # 멀티플레이어 여부

        self.item_list = ["bomb", "clock"]  # 가능한 아이템 종류
        self.my_item_list = deque([])  # 아이템 보유 리스트, popleft 로 선입선출 사용
        self.clock_used = False  # 클락 아이템 사용 여부
        self.clock_count = tv.BASE_CLOCK_COUNT  # 30초, 이벤트는 0.05초마다 생성

        self.score = 0
        self.level = 1
        self.goal = self.level * 5
        self.freeze_time_count = tv.BASE_FREEZE_COUNT  # 미노가 바닥에 닿았을 때 카운트
        self.is_hard_dropped = False  # 현재 미노를 하드드롭 했는지 여부, freeze 관련해서 필요한 변수

        # self.display_update_required = True  # 현재는 구현을 안 해놨지만, 화면 갱신이 필요할 때만 True 로 변경되는 방법을 생각해볼 수 있음.

        self.x = 3  # current mino 위치
        self.y = 0
        self.rotation = 0  # current mino 회전 인덱스
        self.move_down_count = tv.BASE_MOVE_DOWN_COUNT  # 레벨 1일 때의 값. 타이머 이벤트가 5번 발생시 하강. 타이머 이벤트는 0.05 초마다

        self.current_mino = new_mino()  # 현재 미노 초기화
        self.next_mino = new_mino()  # 다음 미노 초기화

        self.is_hold_used = False  # Hold 여부. 연달아가며 계속 hold 하는 꼼수 방지
        self.hold_mino = None  # Hold 한 mino

        self.status = 'start_screen'  # start_screen, in_game, pause, game_over 등

        # self.former_time = None  # 디버그용
        # self.current_time = None  # 디버그용

    def reset(self):
        self.__init__()

    # ############## 이하 상태 ##############
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
        mod = 1  # 변화값
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

    # 바닥 충돌 판정
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

    # move 이벤트 wrapper. 현재 미노가 회전하거나 움직이는 이벤트는 이 래퍼 안에서 동작해야함.
    def move(self, func):
        self.board.temp_matrix = copy.deepcopy(self.board.frozen_matrix)
        func()
        self.board.temp_matrix = self.draw_current_mino(self.board.temp_matrix)
        self.display_update()

    @staticmethod
    def display_update():
        post_event('DISPLAY_UPDATE_REQUIRED')

    # ############ 이하 이벤트 핸들러가 다루는 메소드 #############
    def ev_hard_drop(self):
        self.hard_drop()
        self.is_hard_dropped = True

    def ev_timer_event(self):
        # 디버그용 주석
        # if self.former_time is None:
        #     self.former_time = time.time()
        # self.current_time = time.time()
        #
        # print(f'{self.current_time - self.former_time} \n {self.move_down_count=}')
        #
        # self.former_time = self.current_time
        self.count_move_down()
        self.count_item_clock()

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
            post_event("MOVE")

    def ev_move_right(self):
        if not self.is_right_collide():
            self.move(self.move_right)
            post_event("MOVE")

    # 우측 회전, mod_list 는 현재 미노의 x, y 값을 조금씩 조정했을 때 회전이 가능한지를 판별하기 위함.
    def ev_rotate_right(self):
        mod_list = [0, -1, 1, -2, 2]
        for mod in mod_list:
            if self.is_rotatable(self.x, self.y + mod, 'r'):
                self.rotate(y_mod=mod, right_or_left='r')
                break
            elif self.is_rotatable(self.x + mod, self.y, 'r'):
                self.rotate(x_mod=mod, right_or_left='r')
                break
        self.display_update()

    def ev_rotate_left(self):
        pass

    def ev_hold_current_mino(self):
        if not self.is_hold_used:
            self.move(self.hold_current_mino)

    def ev_pause_game(self):
        if self.status == 'in_game':
            self.status = 'pause'
        elif self.status == 'pause':
            self.status = 'in_game'

    def ev_use_item(self):
        self.move(self.use_item)
    # ############ 이하 동작 메소드 #############
    def move_down(self):
        self.y += 1
        self.move_down_count_reset()

    def move_down_count_reset(self):
        if self.clock_used:
            self.move_down_count = (tv.BASE_MOVE_DOWN_COUNT + 1 - self.level) * 2
        else:
            self.move_down_count = tv.BASE_MOVE_DOWN_COUNT + 1 - self.level

    # 하강 카운트
    def count_move_down(self):
        self.move_down_count -= 1
        if self.move_down_count < 0:
            self.ev_move_down()

    def move_left(self):
        self.x -= 1

    def move_right(self):
        self.x += 1

    def plus_y(self):
        self.y += 1

    # 바닥에 충돌하기 전까지 한 칸씩 하강 반복
    def hard_drop(self):
        while not self.is_bottom_collide(self.x, self.y):
            self.move(self.move_down)
        self.freeze_current_mino()
        post_event("HARD_DROP")

    # 현재 미노를 hold
    def hold_current_mino(self):
        self.is_hold_used = True
        if self.hold_mino is None:
            self.hold_mino = self.current_mino
            self.change_to_next_mino()
        else:
            self.freeze_time_count = tv.BASE_FREEZE_COUNT
            self.x, self.y = 3, 0
            self.current_mino, self.hold_mino = self.hold_mino, self.current_mino

    def pause_game(self):
        pass

    # 회전, 우회전 'r', 좌회전 'l', 기본값은 'r', x_mod, y_mod 는 현재 미노 위치 기준으로 움직였을 때의 가능 여부 판별을 위해 있음.
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

    # freeze 후, 라인 완성됐는지 확인, 제거.
    def check_lines(self):
        line_count = 0

        for y in range(21):  # matrix y 사이즈
            if self.is_y_line_full(y_index=y):  # line 이 full 이면 line count 값 1 더하고 라인 지움
                line_count += 1
                self.erase_line(y_index=y)
                if line_count == 1:
                    post_event("LINE_ERASED")
                elif line_count == 2:
                    post_event("LINE_ERASED_2")
                elif line_count == 3:
                    post_event("LINE_ERASED_3")
                elif line_count == 4:
                    post_event("LINE_ERASED_4")

        score_list = (50, 150, 350, 1000)  # 분리 필요

        if line_count != 0:  # 지운 라인이 있으면 점수, 골 업데이트
            self.update_score(score_list[line_count - 1] * self.level)
            self.update_goal(line_count)

    # 특정 y 라인이 가득 찼는지 여부 반환
    def is_y_line_full(self, y_index: int) -> bool:
        for x in range(10):  # matrix x 사이즈
            if self.board.temp_matrix[x][y_index] == 0:  # 0 은 비어있는 칸을 의미
                return False  # 빈 칸이 나오는 순간 False 반환
        return True  # 빈 칸이 나오지 않고 for 문이 완료되면 True 반환

    # 특정 y 라인 위에 있는 줄을 전부 한 줄 씩 끌어내림.
    def erase_line(self, y_index: int):
        while y_index > 0:
            for x in range(10):  # matrix x 사이즈
                self.board.frozen_matrix[x][y_index] = self.board.frozen_matrix[x][y_index - 1]
                self.board.temp_matrix[x][y_index] = self.board.temp_matrix[x][y_index - 1]
            y_index -= 1

    # 점수 더하기
    def update_score(self, to_add: int):
        self.score += to_add

    # 바닥에 닿았을 때 카운트.
    def bottom_count(self):
        if self.is_hard_dropped or self.freeze_time_count < 0:  # 바닥에 닿아도 6틱동안 움직일수 있음
            self.freeze_current_mino()
        else:
            self.freeze_time_count -= 1

    # 현재 미노를 freeze
    def freeze_current_mino(self):
        self.check_lines()
        self.board.frozen_matrix = copy.deepcopy(self.board.temp_matrix)  # 임시 matrix 를 frozen matrix 로
        self.is_hard_dropped = False  # 다음 미노로 변경됐으니 하드드롭 여부 False
        self.freeze_time_count = tv.BASE_FREEZE_COUNT  # freeze count 초기화
        self.update_score(10 * self.level)  # 블럭 하나 freeze 때 마다 기본 점수 10*레벨
        if self.is_stackable():  # 다음 미노가 나올 수 있는지 판정
            self.change_to_next_mino()
            self.rotation = 0
            self.is_hold_used = False  # 새 미노가 나왔으니 hold 사용 여부 초기화
        else:
            self.status = 'game_over'

    # 라인 수만큼 현재 goal 감소
    def update_goal(self, line_count: int):
        self.goal -= line_count
        if self.goal < 0:
            self.level += 1
            self.goal += self.level * 5
            self.my_item_list.append(choice(self.item_list))  # random.choice
            print(self.my_item_list)

    #         TODO: : my_item blit 띄우기

    def change_to_next_mino(self):
        self.x = 3
        self.y = 0
        self.rotation = 0
        self.freeze_time_count = tv.BASE_FREEZE_COUNT
        self.current_mino = self.next_mino
        self.next_mino = new_mino()
        self.draw_current_mino(self.board.temp_matrix)

    def draw_current_mino(self, matrix):
        grid = self.current_mino.shape[self.rotation]
        tx, ty = self.x, self.y
        while not self.is_bottom_collide(tx, ty):  # 고스트
            ty += 1
        for i in range(4):
            for j in range(4):
                if grid[i][j] != 0:
                    # update ghost
                    matrix[tx + j][ty + i] = 8
                    # update current mino
                    matrix[self.x + j][self.y + i] = grid[i][j]
        return matrix

    # todo bgm 은 게임 인스턴스에서 재생하면 안 될듯합니다.
    # todo bgm 재생이 끝나도 무한 반복
    # def play_bgm(self):
    #     self.bgm = UI_VARIABLES.bgm_list[self.level - 1]
    #     pygame.mixer.music.load(self.bgm)
    #     pygame.mixer.music.play()

    def use_item(self):
        if self.my_item_list:
            used_item = self.my_item_list.popleft()  # 먼저 들어온 순서대로 아이템 사용
            if used_item == "bomb":
                self.item_bomb()
            elif used_item == "clock":
                self.item_clock()
        else:
            post_event('NO_ITEM_REMAIN')

    def item_bomb(self):
        print('bomb used')
        self.erase_line(20)  # 맨 아랫줄 제거, 화면 업데이트는 self.move() 래퍼 안에서 돌리면 해결됩니다. ev_use_item() 메소드에 넣었습니다.
        post_event('BOMB_USED')

    def item_clock(self):
        if self.clock_used:
            print('already_used')
            post_event('NO_ITEM_REMAIN')
        else:
            self.clock_used = True
            post_event('CLOCK_USED')

    def count_item_clock(self):
        if self.clock_used and self.clock_count > 0:
            self.clock_count -= 1
        elif self.clock_count <= 0:
            self.clock_used = False
            self.clock_count = tv.BASE_MOVE_DOWN_COUNT

    # 게임 오버시
    def on_game_over(self):
        self.reset()
