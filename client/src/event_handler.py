from .game_instance import GameInstance
from .display_drawer import DisplayDrawer
import pygame
from pygame.locals import *
from .consts.custom_events import custom_events, custom_events_reversed
from .components.sounds import SOUNDS


class EventFlags:
    def __init__(self):
        self.buffer = 3
        self.dict = {
            'down': self.buffer,
            'up': self.buffer,
            'right': self.buffer,
            'left': self.buffer,
            'hard_drop': self.buffer,
            'pause': self.buffer,
            'hold': self.buffer,
            'use_item': self.buffer
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
            'hold': game_instance.ev_hold_current_mino,
            'use_item': game_instance.ev_use_item,
        }


# 1인플레이시 키맵
class EventKeyMap:
    def __init__(self):
        self.dict = {
            K_DOWN: 'down',
            K_UP: 'up',
            K_RIGHT: 'right',
            K_LEFT: 'left',
            K_SPACE: 'hard_drop',
            K_ESCAPE: 'pause',
            K_LSHIFT: 'hold',
            K_LCTRL: 'use_item'
        }


# 로직 2인용 멀티플레이 키맵
class DualPlayerOneEventKeyMap:
    def __init__(self):
        self.dict = {
            K_s: 'down',
            K_w: 'up',
            K_d: 'right',
            K_a: 'left',
            K_ESCAPE: 'pause',
            K_f: 'hard_drop',
            K_g: 'hold',
            K_h: 'use_item'
        }


class DualPlayerTwoEventKeyMap:
    def __init__(self):
        self.dict = {
            K_DOWN: 'down',
            K_UP: 'up',
            K_RIGHT: 'right',
            K_LEFT: 'left',
            K_ESCAPE: 'pause',
            K_LESS: 'hard_drop',
            K_GREATER: 'hold',
            K_SLASH: 'use_item'
        }


class EventHandler:
    def __init__(self, game_instance: GameInstance, display_drawer: DisplayDrawer):
        self.game_instance = game_instance
        self.display_drawer = display_drawer
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

        self.custom_event_init()

        self.quit = False

    def custom_event_init(self):
        map(pygame.event.Event, custom_events.items())  # pygame 이벤트 등록
        # map(pygame.event.Event, sound_play_events.items())  # pygame 이벤트 등록

        allowed_list = [QUIT, KEYUP, KEYDOWN, USEREVENT, VIDEORESIZE]
        allowed_list.extend(list(custom_events.values()))
        # allowed_list.extend(list(sound_play_events.values()))

        pygame.event.set_allowed(allowed_list)  # 처리할 이벤트 종류 제한

    # main 이 event 를 넘겨주는 메소드
    def handle_event(self, event):
        # self.event_flags dict 의 key 별 bool 값을 확인하여 사이클마다 실행,
        if event.type == USEREVENT:  # 타이머 이벤트임. main.py __init__ 참조
            self.on_timer_event()
            self.execute_event()
            self.check_key_held()

        elif event.type == custom_events['DISPLAY_UPDATE_REQUIRED']:  # 화면 업데이트
            # self.display_drawer.update_display()
            pass
        elif event.type == KEYDOWN:  # 키 입력 이벤트. KEYDOWN은 키가 눌렸을 때, KEYUP은 키가 눌린 후 다시 올라왔을때
            self.on_key_down_event(event)
        elif event.type == KEYUP:
            self.on_key_up_event()
        elif event.type in custom_events.values():
            self.play_sfx(event.type)
        elif event.type == QUIT:  # 종료시
            # 멀티플레이시 소켓 먼저 닫아야할듯함.
            self.quit = True
        # elif event.type == VIDEORESIZE:


    # key_hold 꾹 누르기 체크
    def check_key_held(self):
        if self.game_instance.status == 'in_game':
            key_held = pygame.key.get_pressed()
            for key in self.event_key_map.keys():  # event_key_map 의 모든 키를 확인
                if key_held[key]:
                    flag = self.event_key_map[key]  # key 에 매핑된 flag
                    self.event_flags[flag] -= 1

    # event flag 확인 후 매핑 된 펑션 실행
    def execute_event(self):
        if self.game_instance.status == 'in_game':
            for flag_type in self.event_flags.keys():
                if self.event_flags[flag_type] < 0:
                    self.event_func_map[flag_type]()
                    # self.event_flags[flag_type] = False  # 실행 후에는 플래그 초기화

    # key down event 처리
    def on_key_down_event(self, event):
        try:
            if self.game_instance.status == 'in_game':
                todo = self.event_key_map[event.key]
                self.event_func_map[todo]()
            elif self.game_instance.status == 'pause':
                self.game_instance.ev_pause_game()
            elif self.game_instance.status == 'start_screen':
                self.game_instance.status = 'in_game'
            elif self.game_instance.status == 'game_over':
                self.game_instance.on_game_over()
        except KeyError:
            # print(f'매핑되지 않은 키: {event.key=}')  # 디버그용 주석
            pass

    # key_up 시 버퍼 초기화
    def on_key_up_event(self):
        for key in self.event_flags.keys():
            self.event_flags[key] = self.event_flags_obj.buffer

    # 타이머 이벤트
    def on_timer_event(self):
        if self.game_instance.status == 'in_game':
            self.game_instance.ev_timer_event()

    @staticmethod
    def play_sfx(event_type):
        event = custom_events_reversed.get(event_type)
        if event == "BOMB_USED":
            pygame.mixer.Sound.play(SOUNDS.sfx_bomb)
        elif event == "CLOCK_USED":
            pygame.mixer.Sound.play(SOUNDS.sfx_clock)
        elif event == "NO_ITEM_REMAIN":
            pygame.mixer.Sound.play(SOUNDS.sfx_no_item)

        elif event == "LINE_ERASED":
            pygame.mixer.Sound.play(SOUNDS.sfx_single)
        elif event == "LINE_ERASED_2":
            pygame.mixer.Sound.play(SOUNDS.sfx_double)
        elif event == "LINE_ERASED_3":
            pygame.mixer.Sound.play(SOUNDS.sfx_triple)
        elif event == "LINE_ERASED_4":
            pygame.mixer.Sound.play(SOUNDS.sfx_tetris)

        elif event == "MOVE":
            pygame.mixer.Sound.play(SOUNDS.sfx_move)
