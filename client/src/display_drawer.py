import pygame

from .components import draw_function
from .consts.strings import STRINGS
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
            return pygame.display.set_mode((UI_CONSTS.init_screen_width_multiplayer, UI_CONSTS.init_screen_height),
                                           pygame.RESIZABLE | pygame.HWSURFACE | pygame.DOUBLEBUF | pygame.SCALED)
        else:
            return pygame.display.set_mode((UI_CONSTS.init_screen_width, UI_CONSTS.init_screen_height),
                                           pygame.RESIZABLE | pygame.HWSURFACE | pygame.DOUBLEBUF | pygame.SCALED)

    # self.game_instance.status 확인하여 디스플레이 업데이트
    def update_display(self):
        if self.game_instance.status == 'in_game' or self.game_instance.status == 'game_over':
            self.draw_in_game_screen()
        elif self.game_instance.status == 'pause':
            self.draw_pause()
        elif self.game_instance.status == 'start_screen':
            self.draw_start_screen()
        elif self.game_instance.status == 'mp_game_ready':
            self.draw_message(STRINGS.mp_start_soon)
        elif self.game_instance.status == 'mp_hello':
            self.draw_message(STRINGS.mp_hello)
        elif self.game_instance.status == 'mp_waiting':
            self.draw_message(STRINGS.mp_waiting)
        elif self.game_instance.status == 'mp_approaching':
            self.draw_message(STRINGS.mp_approaching)
        elif self.game_instance.status == 'mp_win':
            self.draw_message(STRINGS.mp_win)
        elif self.game_instance.status == 'mp_lose':
            self.draw_message(STRINGS.mp_lose)

        pygame.display.update()

    def draw_message(self, message):
        self.screen.fill(UI_CONSTS.grey_3)
        message = FONTS.h2_b.render(message, True, UI_CONSTS.white)
        self.screen.blit(message, (0, 120))

    def draw_start_screen(self):
        self.screen.fill(UI_CONSTS.white)
        pygame.draw.rect(
            self.screen,
            UI_CONSTS.grey_1,
            Rect(UI_CONSTS.init_rect_x, UI_CONSTS.init_rect_y, UI_CONSTS.init_screen_width, UI_CONSTS.init_rect_height)
        )  # 아마도 하단 검정 박스
        title = FONTS.h1.render(STRINGS.title, True, UI_CONSTS.grey_1)
        title_info = FONTS.h6.render(STRINGS.copyright, True, UI_CONSTS.white)

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
        pause_message = FONTS.h2_b.render(STRINGS.pause, True, UI_CONSTS.white)
        self.draw_in_game_screen()
        self.screen.blit(pause_message, (62, 105))

    # 게임 오버시 텍스트 오버레이 출력
    def draw_game_over(self):
        over_text_1 = FONTS.h2_b.render(STRINGS.game, True, UI_CONSTS.white)
        over_text_2 = FONTS.h2_b.render(STRINGS.over, True, UI_CONSTS.white)
        # over_start = UI_VARIABLES.h5.render("Press return to continue", 1, UI_VARIABLES.white)
        self.draw_in_game_screen()
        self.screen.blit(over_text_1, (58, 75))
        self.screen.blit(over_text_2, (62, 105))
