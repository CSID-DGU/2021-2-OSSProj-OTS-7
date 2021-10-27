from client.src.game_instance import GameInstance
import pygame
from pygame.locals import *


class EventFlags:
    def __init__(self):
        self.buffer = 5
        self.dict = {
            'down': False,
            'up': False,
            'right': False,
            'left': False,
            'hard_drop': False,
            'pause': False,
            'hold': False,
        }

    def reset(self):
        self.__init__()


class EventFuncMap:
    def __init__(self, game_instance: GameInstance):
        self.dict = {
            'down': game_instance.ev_move_down,
            'up': game_instance.ev_rotate_right,
            'right': game_instance.ev_move_right,
            'left': game_instance.ev_move_left,
            'hard_drop': game_instance.hard_drop,
            'pause': game_instance.ev_pause_game,
            'hold': game_instance.ev_hold_current_mino
        }


class EventKeyMap:
    def __init__(self):
        self.dict = {
            K_DOWN: 'down',
            K_UP: 'up',
            K_RIGHT: 'right',
            K_LEFT: 'left',
            K_SPACE: 'hard_drop',
            K_ESCAPE: 'pause',
            K_LSHIFT: 'hold'
        }


class EventHandler:
    def __init__(self, game_instance: GameInstance):
        self.game_instance = game_instance
        # if multiplayer:
        #     self.mp_game_instance = mp_game_instance
        #     self.mp_ev_flags = mp_ev_flags
        #     self.mp_ev_map = mp_ev_map
        self.event_flags_obj = EventFlags()
        self.event_flags: dict = self.event_flags_obj.dict

        self.event_func_map_obj = EventFuncMap(self.game_instance)
        self.event_func_map: dict = self.event_func_map_obj.dict

        self.event_key_map_obj = EventKeyMap()
        self.event_key_map: dict = self.event_key_map_obj.dict

        self.quit = False

    # main 이 event 를 넘겨주는 메소드
    def handle_event(self, event):
        # self.event_flags dict 의 key 별 bool 값을 확인하여 사이클마다 실행,
        if event.type == USEREVENT:  # 타이머 이벤트임. main.py __init__ 참조
            self.on_timer_event()
        elif event.type == KEYDOWN:  # 키 입력 이벤트. KEYDOWN은 키가 눌렸을 때, KEYUP은 키가 눌린 후 다시 올라왔을때
            self.on_key_down_event(event)
        elif event.type == KEYUP:
            self.on_key_up_event()
        elif event.type == QUIT:  # 종료시
            # 멀티플레이시 소켓 먼저 닫아야할듯함.
            self.quit = True

        self.check_key_held()
        self.execute_event()

    # key_hold 꾹 누르기 체크
    def check_key_held(self):
        if self.game_instance.status == 'in_game':
            key_held = pygame.key.get_pressed()
            for key in self.event_key_map.keys():  # event_key_map 의 모든 키를 확인
                if key_held[key]:
                    flag = self.event_key_map[key]  # key 에 매핑된 flag
                    if self.event_flags_obj.buffer < 0:  # 기본 버퍼는 5, 버퍼가 음수일시 연속 키 입력
                        self.event_flags[flag] = True  # 매핑된 flag True 로 변경
                    else:
                        self.event_flags_obj.buffer -= 1

    # event flag 확인 후 매핑 된 펑션 실행
    def execute_event(self):
        for flag_type in self.event_flags.keys():
            if self.event_flags[flag_type]:
                self.event_func_map[flag_type]()
                self.event_flags[flag_type] = False  # 실행 후에는 플래그 False 로 변경

    # key down event 처리
    def on_key_down_event(self, event):
        if self.game_instance.status == 'in_game':
            todo = self.event_key_map[event.key]
            self.event_func_map[todo]()
            self.event_flags_obj.buffer = 5  # 버퍼 초기화
        elif self.game_instance.status == 'pause':
            self.game_instance.ev_pause_game()
        elif self.game_instance.status == 'start_screen':
            self.game_instance.status = 'in_game'
        elif self.game_instance.status == 'game_over':
            self.game_instance.on_game_over()

    # key_up 시 버퍼 초기화
    def on_key_up_event(self):
        self.event_flags_obj.buffer = 5

    # 타이머 이벤트
    def on_timer_event(self):
        if self.game_instance.status == 'in_game':
            self.game_instance.count_move_down()
