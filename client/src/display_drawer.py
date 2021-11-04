import pygame

from .components import draw_function
from .variables.ui_variables import UI_VARIABLES
from pygame import Rect


class DisplayDrawer:
    def __init__(self, game_instance, multiplayer_instance=None):
        self.game_instance = game_instance
        self.multiplayer_instance = multiplayer_instance
        self.screen = self.get_screen()
        self.fake_screen = self.screen.copy()

    # 싱글플레이 멀티플레이 화면 크기
    def get_screen(self):
        if self.multiplayer_instance is not None:
            return pygame.display.set_mode((UI_VARIABLES.init_screen_width * 2, UI_VARIABLES.init_screen_height), pygame.RESIZABLE | pygame.HWSURFACE | pygame.DOUBLEBUF| pygame.SCALED)
        else:
            return pygame.display.set_mode((UI_VARIABLES.init_screen_width, UI_VARIABLES.init_screen_height), pygame.RESIZABLE | pygame.HWSURFACE | pygame.DOUBLEBUF | pygame.SCALED)

    # self.game_instance.status 확인하여 디스플레이 업데이트
    def update_display(self):
        if self.game_instance.status == 'in_game':
            self.draw_in_game_screen()
        elif self.game_instance.status == 'game_over':
            self.draw_game_over()
        elif self.game_instance.status == 'pause':
            self.draw_pause()
        elif self.game_instance.status == 'start_screen':
            self.draw_start_screen()
        pygame.display.update()

    def draw_start_screen(self):  # TODO start screen 멀티플레이 선택, 웹 연결 등
        self.screen.fill(UI_VARIABLES.white)
        pygame.draw.rect(
            self.screen,
            UI_VARIABLES.grey_1,
            Rect(UI_VARIABLES.init_rect_x, UI_VARIABLES.init_rect_y, UI_VARIABLES.init_screen_width, UI_VARIABLES.init_rect_height)
        )  # 아마도 하단 검정 박스
        title = UI_VARIABLES.h1.render("PYTRIS™", 1, UI_VARIABLES.grey_1)
        title_start = UI_VARIABLES.h5.render("Press space to start", 1, UI_VARIABLES.white)
        title_info = UI_VARIABLES.h6.render("Copyright (c) 2017 Jason Kim All Rights Reserved.", 1,
                                            UI_VARIABLES.white)

        self.screen.blit(title, (65, 120))
        self.screen.blit(title_info, (40, 335))

    # game_instance 의 status 가 in_game 일 때 렌더링. components.draw_function.py 참조
    def draw_in_game_screen(self):
        if self.multiplayer_instance is not None:
            draw_function.draw_in_game_screen(self.game_instance, self.screen, self.multiplayer_instance)
        else:
            draw_function.draw_in_game_screen(self.game_instance, self.screen)

    # 멀티플레이어 로비.
    def draw_multiplayer_lobby(self):
        pass

    # 일시정지 시 PAUSE 글씨 출력
    def draw_pause(self):
        pause_message = UI_VARIABLES.h2_b.render("PAUSE", 1, UI_VARIABLES.white)
        self.draw_in_game_screen()
        self.screen.blit(pause_message, (62, 105))

    # 게임 오버시 텍스트 오버레이 출력
    def draw_game_over(self):
        over_text_1 = UI_VARIABLES.h2_b.render("GAME", 1, UI_VARIABLES.white)
        over_text_2 = UI_VARIABLES.h2_b.render("OVER", 1, UI_VARIABLES.white)
        # over_start = UI_VARIABLES.h5.render("Press return to continue", 1, UI_VARIABLES.white)
        self.draw_in_game_screen()
        self.screen.blit(over_text_1, (58, 75))
        self.screen.blit(over_text_2, (62, 105))
