import pygame

from client.src.components import draw_function
from client.src.variables.ui_variables import UI_VARIABLES
from pygame import Rect


class DisplayDrawer:
    def __init__(self, game_instance):
        self.game_instance = game_instance
        self.is_multiplayer = self.game_instance.is_multiplayer
        self.screen = self.get_screen()

    def get_screen(self):
        if self.game_instance.is_multiplayer:
            return pygame.display.set_mode((600, 374))
        else:
            return pygame.display.set_mode((300, 374))

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
            Rect(0, 187, 300, 187)
        )
        title = UI_VARIABLES.h1.render("PYTRIS™", 1, UI_VARIABLES.grey_1)
        title_start = UI_VARIABLES.h5.render("Press space to start", 1, UI_VARIABLES.white)
        title_info = UI_VARIABLES.h6.render("Copyright (c) 2017 Jason Kim All Rights Reserved.", 1,
                                            UI_VARIABLES.white)

        # TODO title start 글씨 깜빡이게

        self.screen.blit(title, (65, 120))
        self.screen.blit(title_info, (40, 335))

    def draw_in_game_screen(self):
        draw_function.draw_in_game_screen(self.game_instance.next_mino,
                                          self.game_instance.hold_mino,
                                          self.game_instance.score,
                                          self.game_instance.level,
                                          self.game_instance.goal,
                                          self.screen,
                                          self.game_instance.board.temp_matrix)

    def draw_multiplayer_lobby(self):
        pass

    def draw_pause(self):
        pause_message = UI_VARIABLES.h2_b.render("PAUSE", 1, UI_VARIABLES.white)
        self.draw_in_game_screen()
        self.screen.blit(pause_message, (62, 105))

    def draw_game_over(self):
        over_text_1 = UI_VARIABLES.h2_b.render("GAME", 1, UI_VARIABLES.white)
        over_text_2 = UI_VARIABLES.h2_b.render("OVER", 1, UI_VARIABLES.white)
        over_start = UI_VARIABLES.h5.render("Press return to continue", 1, UI_VARIABLES.white)
        self.draw_in_game_screen()
        self.screen.blit(over_text_1, (58, 75))
        self.screen.blit(over_text_2, (62, 105))
