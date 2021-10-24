import pygame
from client.src.event_handler import EventHandler
from client.src.game_instance import GameInstance
from client.src.display_drawer import DisplayDrawer


class OTS:
    def __init__(self, is_multiplayer=False):
        self.is_multiplayer = is_multiplayer

        self.clock = pygame.time.Clock()
        self.running = True

        self.game_session = GameInstance(self.is_multiplayer)  # 게임 로직, 상태 등 처리
        self.event_handler = EventHandler(self.game_session)  # 키 입력, 타이머 등 이벤트 처리
        self.display_drawer = DisplayDrawer(self.game_session)  # 화면 업데이트 처리

        self.pygame = pygame

        pygame.init()
        pygame.time.set_timer(pygame.USEREVENT, 50)  # 0.05초마다 이벤트 생성
        pygame.display.set_caption("OTS")

    def run_game(self):
        self.main_loop()

    def main_loop(self):
        while self.running:
            # 이벤트 처리
            for event in pygame.event.get():
                self.handle_event(event)

            # 화면 출력 업데이트

            self.display_drawer.update_display()
            self.clock.tick(60)  # 60hz

    def handle_event(self, event):
        self.event_handler.handle_event(event)
