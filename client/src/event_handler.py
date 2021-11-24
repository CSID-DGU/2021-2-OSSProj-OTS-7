from .game_instance import GameInstance
from .display_drawer import DisplayDrawer
import pygame
from pygame.locals import *
from .consts.custom_events import CUSTOM_EVENTS, CUSTOM_EVENTS_REVERSED
from .sound_player import SoundPlayer


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
            'down': game_instance.ev_move_down_manual,
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

        self.sound_player = SoundPlayer()

        self.event_func_map_obj = EventFuncMap(self.game_instance)
        self.event_func_map: dict = self.event_func_map_obj.dict

        self.event_key_map_obj = EventKeyMap()
        self.event_key_map: dict = self.event_key_map_obj.dict

        self.custom_event_init()

        self.quit = False

    @staticmethod
    def custom_event_init():
        map(pygame.event.Event, CUSTOM_EVENTS.items())  # pygame 이벤트 등록
        # map(pygame.event.Event, sound_play_events.items())  # pygame 이벤트 등록

        allowed_list = [QUIT, KEYUP, KEYDOWN, USEREVENT, VIDEORESIZE]
        allowed_list.extend(list(CUSTOM_EVENTS.values()))
        # allowed_list.extend(list(sound_play_events.values()))

        pygame.event.set_allowed(allowed_list)  # 처리할 이벤트 종류 제한

    # main 이 event 를 넘겨주는 메소드
    def handle_event(self, event):
        # self.event_flags dict 의 key 별 bool 값을 확인하여 사이클마다 실행,
        if event.type == USEREVENT:  # 타이머 이벤트임. main.py __init__ 참조
            self.on_timer_event()
            self.execute_event()
            self.check_key_held()

        # elif event.type == CUSTOM_EVENTS['DISPLAY_UPDATE_REQUIRED']:  # 화면 업데이트
        #     # self.display_drawer.update_display()
        #     pass
        elif event.type == KEYDOWN:  # 키 입력 이벤트. KEYDOWN은 키가 눌렸을 때, KEYUP은 키가 눌린 후 다시 올라왔을때
            self.on_key_down_event(event)
        elif event.type == KEYUP:
            self.on_key_up_event()
        elif event.type == QUIT:  # 종료시
            # 멀티플레이시 소켓 먼저 닫아야할듯함.
            self.quit = True
        elif event.type == CUSTOM_EVENTS['GAME_START']:
            self.sound_player.update_bgm(self.game_instance.level)
        elif event.type == CUSTOM_EVENTS['LEVEL_UP']:
            self.on_level_up()
        elif event.type == CUSTOM_EVENTS['GAME_OVER']:
            self.on_game_over()
        elif event.type == CUSTOM_EVENTS['PAUSE']:
            self.on_pause()
        elif event.type == CUSTOM_EVENTS['UNPAUSE']:
            self.on_unpause()
        elif event.type in CUSTOM_EVENTS.values():
            self.play_sfx(event.type)

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
        if self.game_instance.status == 'in_game':
            try:
                todo = self.event_key_map[event.key]
                self.event_func_map[todo]()
            except KeyError:
                # print(f'매핑되지 않은 키: {event.key=}')  # 디버그용 주석
                pass
        elif self.game_instance.status == 'pause' and event.key == K_ESCAPE:
            self.game_instance.ev_unpause_game()
        elif self.game_instance.status == 'start_screen':
            self.game_instance.ev_game_start()
        elif self.game_instance.status == 'game_over' and event.key == K_SPACE:
            self.game_instance.ev_game_over_screen_out()

    # key_up 시 버퍼 초기화
    def on_key_up_event(self):
        for key in self.event_flags.keys():
            self.event_flags[key] = self.event_flags_obj.buffer

    # 타이머 이벤트
    def on_timer_event(self):
        if self.game_instance.status == 'in_game':
            self.game_instance.ev_timer_event()

    # 레벨 업 이벤트 처리
    def on_level_up(self):
        level = self.game_instance.level
        self.game_instance.level_up()
        self.sound_player.update_bgm(level)

    # 게임 오버 이벤트 처리
    def on_game_over(self):
        self.sound_player.stop_music()

    # 일시정지 이벤트
    def on_pause(self):
        self.sound_player.pause_bgm()

    # 일시정지 해제 이벤트
    def on_unpause(self):
        self.sound_player.unpause_bgm()

    # 효과음 재생
    def play_sfx(self, event_type):
        to_play = CUSTOM_EVENTS_REVERSED.get(event_type)
        self.sound_player.play_sfx(to_play)
