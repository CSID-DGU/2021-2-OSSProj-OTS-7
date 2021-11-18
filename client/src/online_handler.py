import websocket
import time
import threading
import json
import pprint
from .game_instance import GameInstance
from .components.mino import Mino
# server side code scheme
# 't': # type
# {
#     't': code,
#     'd': data
# }
# type list -send
# t == 'gd':  # game data
# t == 'go':  # game over
# t == 'wa':  # waiting add
# t == 'wr':  # waiting remove
# t == 'a':  # approach
# t == 'ac':  # approach cancel
# t == 'aa':  # host accept
# t == 'ar':  # host reject


def on_error(ws, error):
    print(error)


def on_close(ws, close_status_code, close_msg):
    print("### closed ###")


class OnlineHandler:
    def __init__(self, user_id, game_instance: GameInstance, opponent_instance: GameInstance):
        # websocket.enableTrace(True)
        self.status = 'hello'
        self.user_id = user_id
        self.game_instance = game_instance
        self.opponent_instance = opponent_instance
        self.opponent = None
        self.current_waiter_list = []
        self.current_approacher_list = []
        self.ws = websocket.WebSocketApp(
            f"ws://127.0.0.1:8000/ws",
            on_open=lambda ws: self.on_open(ws),
            on_message=lambda ws, msg: self.on_message(ws, msg),
            on_error=on_error,
            on_close=on_close,
        )
        self.ws_thread = threading.Thread(target=self.run_forever, daemon=True)  # 웹 소켓 연결 스레드
        self.send_gd_thread = threading.Thread(target=self.send_current_gd_thread, daemon=True)  # 게임 데이터 전송 스레드

    def on_open(self, ws):
        ws.send(self.user_id)

    def on_message(self, ws, message):
        print(message)
        try:
            raw_data = json.loads(message)  # 최상위 키가 하나 존재하는 딕셔너리 데이터
            print(raw_data)  # 디버그
        except json.JSONDecodeError:
            raw_data = None
            print('message not in json format')

        if raw_data is not None:
            self.parse_data(raw_data)

    def parse_data(self, raw_data):
        # type list -receive
        # 'go': 'opponent_game_over',
        # 'mc': 'match_complete',
        # 'ha': 'host_accepted',
        # 'hr': 'host_rejected',
        # 'al': 'approacher_list',
        # 'wl': 'waiter_list
        # 'lo': 'loser',
        # 'wi': 'winner'
        try:
            t = raw_data['t']
            d = raw_data['d']
        except KeyError:
            t = None
            d = None
            print(f'Cannot parse data:\n{raw_data=}')

        if self.status == 'in_game':
            self.parse_in_game(t, d)
        elif self.status == 'waiting':
            self.parse_waiting(t, d)
        elif self.status == 'approaching':
            self.parse_approaching(t, d)
        elif self.status == 'hello':
            self.parse_hello(t, d)

    def parse_in_game(self, t, d):
        if t == 'gd':  # 게임 데이터일때
            self.update_opponent_info(d)
        elif t == 'lo':  # 패배
            pass  # 패배 화면
        elif t == 'wi':  # 승리
            pass  # 패배 화면
        elif t == 'go':  # 상대 게임 오버
            pass  # 상대 화면에 게임 오버 띄우기
        elif t == 'mc':  # 매치 끝남
            self.game_instance.status = 'mp_waiting'  #

    def update_opponent_info(self, d: dict):
        self.opponent_instance.score = d.get('score')
        self.opponent_instance.level = d.get('level')
        self.opponent_instance.goal = d.get('goal')
        self.opponent_instance.board.temp_matrix = d.get('matrix')
        self.opponent_instance.next_mino = Mino(d.get('next_mino_index'))
        self.opponent_instance.hold_mino = Mino(d.get('hold_mino_index'))

    def parse_waiting(self, t, d):
        if t == 'al':  # 어프로처 리스트
            self.update_current_approacher(d)

    def update_current_approacher(self, d):
        self.current_approacher_list = d

    def parse_approaching(self, t, d):
        if t == 'ha':  # 대결 제안 수락됨
            self.reset_instances()
            self.game_instance.reset()
            self.game_instance.status('mp_game_ready')
            time.sleep(3)
            self.game_instance.status('in_game')
        elif t == 'hr':  # 대결 제안 거절됨
            self.status = 'hello'  # 다시 대기 상태

    def reset_instances(self):
        self.opponent_instance.reset()
        self.game_instance.reset()

    def parse_hello(self, t, d):
        if t == 'wl':
            self.update_current_waiter_list(d)

    def update_current_waiter_list(self, d):
        self.current_waiter_list = d

    def run_forever(self):
        self.is_running = True
        self.ws.run_forever()

    def close(self):
        self.is_running = False
        self.ws.close()

    def send_json_req(self, req):
        self.ws.send(json.dumps(req))

    def waiting_list_add(self):
        req = {
            't': 'wa',
            'd': None
        }
        self.send_json_req(req)

    def waiting_list_remove(self):
        req = {
            't': 'wr',
            'd': None
        }
        self.send_json_req(req)

    def approach(self, waiter_id: str):
        req = {
            't': 'a',
            'd': waiter_id
        }
        self.send_json_req(req)

    def approach_cancel(self):
        pass

    def host_accept(self, approacher_id: str):
        req = {
            't': 'aa',
            'd': approacher_id
        }
        self.send_json_req(req)

    def host_reject(self, approacher_id: str):
        req = {
            't': 'ar',
            'd': approacher_id
        }
        self.send_json_req(req)

    def send_current_gd(self):
        current_dict = {
            # 't': 'gd',
            # 'd': {
            #     'id': self.user_id,
            #     'score': self.game_instance.score,
            #     'level': self.game_instance.level,
            #     'goal': self.game_instance.goal,
            #     'matrix': self.game_instance.board.temp_matrix,
            #     'next_mino_index': self.game_instance.next_mino.shape_index,
            #     'hold_mino_index': self.game_instance.hold_mino.shape_index
            # }
        }
        self.send_json_req(current_dict)

    def send_current_gd_thread(self):
        while True:
            if self.game_instance.status == 'in_game':
                self.send_current_gd()
                time.sleep(0.1)  # 0.1초마다

    def init_send_gd_thread(self):  # 게임 데이터 전송 스레드 초기화
        self.send_gd_thread = threading.Thread(target=self.send_current_gd_thread, daemon=True)

