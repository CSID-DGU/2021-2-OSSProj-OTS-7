import websocket
import time
import threading
import json
from .game_instance import GameInstance
from .components.mino import Mino

# receiving codes
RCODES = {
    'game_data': 'gd',
    'game_over': 'go',
    'match_set': 'ms',
    'match_complete': 'mc',
    'game_start': 'gs',
    'waiter_list': 'wl',
    'host_accepted': 'ha',
    'host_rejected': 'hr',
    'approacher_list': 'al',
    'lose': 'lo',
    'win': 'wi'
}

# sending codes
SCODES = {
    'game_data': 'gd',
    'game_over': 'go',
    'waiting_list_add': 'wa',
    'waiting_list_remove': 'wr',
    'waiting_list_get': 'wg',
    'approach': 'a',
    'approach_cancel': 'ac',
    'host_accept': 'ha',
    'host_reject': 'hr',
}


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
        self.ws_thread = threading.Thread(target=self.ws_connect, daemon=True)  # 웹 소켓 연결 스레드
        self.s_game_data_thread = threading.Thread(target=self.s_game_data_loop, daemon=True)  # 게임 데이터 전송 스레드

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
            self.r_parse_data(raw_data)

    # 웹소켓 연결
    def ws_connect(self):
        self.ws.run_forever()

    # 게임 인스턴스들 초기화
    def reset_instances(self):
        self.opponent_instance.reset()
        self.game_instance.reset()

    # 이하 수신
    # 데이터 parse
    def r_parse_data(self, raw_data):
        try:
            t = raw_data['t']
            d = raw_data['d']
        except KeyError:
            t = None
            d = None
            print(f'Cannot parse data:\n{raw_data=}')

        if self.status == 'in_game':
            self.r_parse_in_game(t, d)
        elif self.status == 'waiting':
            self.r_parse_waiting(t, d)
        elif self.status == 'approaching':
            self.r_parse_approaching(t, d)
        elif self.status == 'hello':
            self.r_parse_hello(t, d)

    # in_game 상황일때
    def r_parse_in_game(self, t, d):
        if t == RCODES['game_data']:  # 게임 데이터일때
            self.r_update_opponent_info(d)
        elif t == RCODES['lose']:  # 패배
            pass  # 패배 화면
        elif t == RCODES['win']:  # 승리
            pass  # 패배 화면
        elif t == RCODES['game_over']:  # 상대 게임 오버
            pass  # 상대 화면에 게임 오버 띄우기
        elif t == RCODES['match_complete']:  # 매치 끝남
            self.r_on_match_complete()

    def r_update_opponent_info(self, d: dict):
        self.opponent_instance.score = d.get('score')
        self.opponent_instance.level = d.get('level')
        self.opponent_instance.goal = d.get('goal')
        self.opponent_instance.board.temp_matrix = d.get('matrix')
        self.opponent_instance.next_mino = Mino(d.get('next_mino_index'))
        self.opponent_instance.hold_mino = Mino(d.get('hold_mino_index'))

    def r_on_match_complete(self):
        self.game_instance.status = 'mp_waiting'

    def r_parse_waiting(self, t, d):
        if t == RCODES['approacher_list']:  # 어프로처 리스트
            self.r_update_current_approacher(d)

    def r_update_current_approacher(self, d):
        self.current_approacher_list = d

    def r_parse_approaching(self, t, d):
        if t == RCODES['host_accepted']:  # 대결 제안 수락됨
            self.reset_instances()
            self.game_instance.reset()
            self.game_instance.status('mp_game_ready')
            time.sleep(3)
            self.game_instance.status('in_game')
        elif t == RCODES['host_rejected']:  # 대결 제안 거절됨
            self.status = 'hello'  # 다시 대기 상태

    def r_parse_hello(self, t, d):
        if t == RCODES['waiter_list']:
            self.r_update_current_waiter_list(d)

    def r_update_current_waiter_list(self, d):
        self.current_waiter_list = d

    # 이하 전송

    def send_json_req(self, req):
        self.ws.send(json.dumps(req))

    def build_and_send_json_req(self, t: str, d=None):
        req = {
            't': t,
            'd': d
        }
        self.send_json_req(req=req)

    def s_waiting_list_add(self):
        self.build_and_send_json_req(SCODES['waiting_list_add'])

    def s_waiting_list_remove(self):
        self.build_and_send_json_req(SCODES['waiting_list_remove'])

    def s_approach(self, waiter_id: str):
        self.build_and_send_json_req(SCODES['approach'], waiter_id)

    def s_approach_cancel(self):
        self.build_and_send_json_req(SCODES['approach_cancel'])

    def s_host_accept(self, approacher_id: str):
        self.build_and_send_json_req(SCODES['host_accept'], approacher_id)

    def s_host_reject(self, approacher_id: str):
        self.build_and_send_json_req(SCODES['host_reject'], approacher_id)

    def s_game_data(self):
        d = {
            'id': self.user_id,
            'score': self.game_instance.score,
            'level': self.game_instance.level,
            'goal': self.game_instance.goal,
            'matrix': self.game_instance.board.temp_matrix,
            'next_mino_index': self.game_instance.next_mino.shape_index,
            'hold_mino_index': self.game_instance.hold_mino.shape_index,
        }
        self.build_and_send_json_req(SCODES['game_data'], d)

    def s_game_data_loop(self):  # 스레드로 사용할것
        while True:
            if self.game_instance.status == 'in_game':
                self.s_game_data()  # 비동기 처리가 필요할수도
                time.sleep(0.1)  # 0.1초마다
            if self.game_instance.status == 'game_over':
                self.build_and_send_json_req(t=SCODES['game_over'], d=None)
                break

    def s_game_data_thread_init(self):  # 게임 데이터 전송 스레드 초기화
        self.s_game_data_thread = threading.Thread(target=self.s_game_data_loop, daemon=True)

    def s_game_data_thread_restart(self):  # 게임 데이터 전송 스레드 재시작
        self.s_game_data_thread_init()
        self.s_game_data_thread.start()
