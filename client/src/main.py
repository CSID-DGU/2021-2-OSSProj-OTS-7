import pygame
import sys
import threading
from client.src.event_handler import EventHandler
from client.src.game_instance import GameInstance
from client.src.display_drawer import DisplayDrawer
from client.src.ot_websocket import OTSWebsocket


class OTS:
    def __init__(self, is_multiplayer=False):
        self.is_multiplayer = is_multiplayer  # 멀티플레이어 여부

        self.clock = pygame.time.Clock()  # 타이머 이벤트 발생기
        self.running = True  # 가동 상태, 현재 이벤트 핸들러에서 pygame.quit()을 이용해 끄게 되는데, 손을 봐야할듯함.

        self.game_session = GameInstance(self.is_multiplayer)  # 게임 로직, 상태 등 처리
        self.event_handler = EventHandler(self.game_session)  # 키 입력, 타이머 등 이벤트 처리
        self.display_drawer = DisplayDrawer(self.game_session)  # 화면 업데이트 처리

        self.pygame = pygame
        if is_multiplayer:
            self.websocket_client = OTSWebsocket(123, self.game_session)
            self.websocket_client.opponent = 456
            self.wsc_thread = threading.Thread(target=self.websocket_client.run_forever, daemon=True)

        pygame.init()  # 파이게임 초기화
        pygame.time.set_timer(pygame.USEREVENT, 50)  # 0.05초마다 이벤트 생성
        pygame.display.set_caption("OTS")  # 창 상단에 표시되는 이름

    def run_game(self):
        if self.is_multiplayer:
            self.wsc_thread.start()
        self.main_loop()

    def main_loop(self):
        while self.running:
            # 이벤트 처리
            for event in pygame.event.get():
                self.handle_event(event)

            if self.is_multiplayer:
                if self.game_session.status == 'in_game' and not self.websocket_client.is_sending_current_json:
                    self.websocket_client.thread_send_current.start()
            # 화면 출력 업데이트
            self.display_drawer.update_display()
            self.clock.tick(60)  # 60hz

            # 게임 종료
            if self.event_handler.quit:
                self.pygame.quit()
                if self.is_multiplayer:
                    self.websocket_client.ws.close()
                sys.exit()

            # 멀티플레이
            if self.is_multiplayer:
                if self.game_session.status == 'game_over':
                    self.websocket_client.is_sending_current_json = False

    # 이벤트 핸들러에 이벤트 넘겨주기
    def handle_event(self, event):
        self.event_handler.handle_event(event)
