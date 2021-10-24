from client.src.game_instance import GameInstance
import pygame
from pygame.locals import *


class EventHandler:
    def __init__(self, game_instance: GameInstance):
        self.game_instance = game_instance

    def handle_event(self, event):
        if event.type == USEREVENT:
            self.on_timer_event()
        elif event.type == KEYDOWN:
            self.on_key_down_event(event)
        elif event.type == QUIT:
            pygame.quit()

    def on_timer_event(self):
        if self.game_instance.status == 'in_game':
            self.game_instance.count_move_down()

    def on_key_down_event(self, event):
        if self.game_instance.status == 'in_game':
            if event.key == K_SPACE:
                self.game_instance.ev_hard_drop()
            elif event.key == K_LEFT:
                self.game_instance.ev_move_left()
            elif event.key == K_RIGHT:
                self.game_instance.ev_move_right()
            elif event.key == K_DOWN:
                self.game_instance.ev_move_down_manual()
            elif event.key == K_UP:
                self.game_instance.ev_rotate_right()
            elif event.key == K_LSHIFT:
                self.game_instance.ev_hold_current_mino()
        elif self.game_instance.status == 'start_screen':
            self.game_instance.status = 'in_game'
        elif self.game_instance.status == 'game_over':
            self.game_instance.on_game_over()
        if event.key == K_ESCAPE:
            self.game_instance.ev_pause_game()

    def on_key_hold_event(self):
        pass

    def on_multiplayer_event(self):
        pass
