import pygame

from .components import draw_function
from .consts.ui_consts import UI_CONSTS
from .components.fonts import FONTS
from pygame import Rect


class DisplayDrawer:
    def __init__(self, game_instance, multiplayer_instance=None):
        self.game_instance = game_instance
        self.multiplayer_instance = multiplayer_instance
        self.screen = self.get_screen()

    # 싱글플레이 멀티플레이 화면 크기
    def get_screen(self):
        if self.multiplayer_instance is not None:
            return pygame.display.set_mode((UI_CONSTS.init_screen_width * 2, UI_CONSTS.init_screen_height),
                                           pygame.RESIZABLE | pygame.HWSURFACE | pygame.DOUBLEBUF | pygame.SCALED)
        else:
            return pygame.display.set_mode((UI_CONSTS.init_screen_width, UI_CONSTS.init_screen_height),
                                           pygame.RESIZABLE | pygame.HWSURFACE | pygame.DOUBLEBUF | pygame.SCALED)

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
        self.screen.fill(UI_CONSTS.white)
        pygame.draw.rect(
            self.screen,
            UI_CONSTS.grey_1,
            Rect(UI_CONSTS.init_rect_x, UI_CONSTS.init_rect_y, UI_CONSTS.init_screen_width, UI_CONSTS.init_rect_height)
        )  # 아마도 하단 검정 박스
        title = FONTS.h1.render("OTS ™", True, UI_CONSTS.grey_1)
        title_start = FONTS.h5.render("Press space to start", True, UI_CONSTS.white)
        title_info = FONTS.h6.render("Copyright (c) 2021 Team OTS All Rights Reserved.", True, UI_CONSTS.white)

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
        pause_message = FONTS.h2_b.render("PAUSE", True, UI_CONSTS.white)
        self.draw_in_game_screen()
        self.screen.blit(pause_message, (62, 105))

    # 게임 오버시 텍스트 오버레이 출력
    def draw_game_over(self):
        over_text_1 = FONTS.h2_b.render("GAME", True, UI_CONSTS.white)
        over_text_2 = FONTS.h2_b.render("OVER", True, UI_CONSTS.white)
        # over_start = UI_VARIABLES.h5.render("Press return to continue", 1, UI_VARIABLES.white)
        self.draw_in_game_screen()
        self.screen.blit(over_text_1, (58, 75))
        self.screen.blit(over_text_2, (62, 105))
