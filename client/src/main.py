import pygame
import sys
import threading
from .event_handler import EventHandler
from .game_instance import GameInstance
from .display_drawer import DisplayDrawer
from .ot_websocket import OTSWebsocket
import time


class OTS:
    def __init__(self, game_mode: str = 'single', player_id: str = 'offline'):
        self.game_mode = game_mode
        self.game_instance = None
        self.multiplayer_instance = None
        if self.game_mode == 'online' or self.game_mode == 'dual':
            self.player_id = player_id
            self.multiplayer_instance = GameInstance()  # 게임 인스턴스 그대로 재활용, 성능상 문제 없으면 그대로 유지해도 무방할듯
            self.game_instance = GameInstance(is_multiplayer=True)  # 게임 로직, 상태 등 처리
        else:
            self.game_instance = GameInstance()

        if self.game_mode == 'online':
            self.websocket_client = OTSWebsocket(self.player_id, self.game_instance, self.multiplayer_instance)
            self.wsc_thread = threading.Thread(target=self.websocket_client.run_forever, daemon=True)  # 웹 소켓 연결 스레드

        self.clock = pygame.time.Clock()  # 타이머 이벤트 발생기
        self.running = True  # 가동 상태, 현재 이벤트 핸들러에서 pygame.quit()을 이용해 끄게 되는데, 손을 봐야할듯함.

        self.display_drawer = DisplayDrawer(self.game_instance, self.multiplayer_instance)  # 화면 업데이트 처리
        self.event_handler = EventHandler(self.game_instance, self.display_drawer)  # 키 입력, 타이머 등 이벤트 처리

        pygame.time.set_timer(pygame.USEREVENT, 50)  # 0.05초마다 이벤트 생성
        pygame.display.set_caption("OTS")  # 창 상단에 표시되는 이름

    # run_client.py 에서 실행함.
    def run_game(self):
        if self.game_mode == 'online':
            self.wsc_thread.start()  # 웹소켓 스레드 시작
            self.websocket_client.thread.start()  # 0.1초마다 게임 정보 보내는 스레드, 추후 변동사항 발생시에만 보내도록 수정 필요
        self.main_loop()

    def main_loop(self):
        while self.running:
            # 이벤트 처리
            for event in pygame.event.get():
                self.handle_event(event)

            # 화면 출력 업데이트
            self.display_drawer.update_display()
            self.clock.tick(60)  # 60hz

            # 게임 종료
            if self.event_handler.quit:
                pygame.display.quit()
                pygame.quit()
                if self.game_mode == 'online':
                    self.websocket_client.ws.close()  # 소켓 해제
                sys.exit()

    # 이벤트 핸들러에 이벤트 넘겨주기
    def handle_event(self, event):
        self.event_handler.handle_event(event)
