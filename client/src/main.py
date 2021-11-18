import pygame
import os
import signal
from .event_handler import EventHandler
from .game_instance import GameInstance
from .display_drawer import DisplayDrawer
from .online_handler import OnlineHandler
TIMER_INTERVAL = 50  # 0.05초마다 이벤트


class OTS:
    def __init__(self, game_instance: GameInstance, event_handler: EventHandler, display_drawer: DisplayDrawer):
        self.game_instance = game_instance
        self.display_drawer = display_drawer
        self.event_handler = event_handler

        self.clock = pygame.time.Clock()  # 타이머 이벤트 발생기
        self.running = True  # 가동 상태, 현재 이벤트 핸들러에서 pygame.quit()을 이용해 끄게 되는데, 손을 봐야할듯함.

        pygame.time.set_timer(pygame.USEREVENT, TIMER_INTERVAL)  # 0.05초마다 이벤트 생성
        pygame.display.set_caption("OTS")  # 창 상단에 표시되는 이름

    def before_run(self):
        pass  # 상속된 객체에서 오버라이드함.

    def run_game(self):
        self.before_run()
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
                self.quit()
    
    def before_quit(self):
        pass  # 상속된 객체에서 오버라이딩
    
    def quit(self):
        self.before_quit()
        pygame.display.quit()
        pygame.quit()
        try:  # 런처 동시 종료를 위함.
            os.kill(os.getpid(), signal.SIGTERM)  # POSIX
        except AttributeError:
            os._exit()  # 윈도우


    # 이벤트 핸들러에 이벤트 넘겨주기
    def handle_event(self, event):
        self.event_handler.handle_event(event)


class OTSONLINE(OTS):
    def __init__(self, game_instance: GameInstance, event_handler: EventHandler, display_drawer: DisplayDrawer, online_handler: OnlineHandler):
        super().__init__(game_instance, event_handler, display_drawer)
        self.online_handler = online_handler

    def before_run(self):
        self.online_handler.ws_thread.start()  # 웹소켓 스레드 시작

    def before_quit(self):
        self.online_handler.ws.close()
