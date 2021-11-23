import websocket
import time
import threading
import asyncio
import json
from .game_instance import GameInstance
from .components.mino import Mino
from .launcher.online_lobby import OnlineLobby
from .launcher.online_data_temp import GuiEmit
from .consts.urls import URLS

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
    def __init__(self, user_id: str,
                 game_instance: GameInstance,
                 opponent_instance: GameInstance,
                 online_lobby: OnlineLobby,
                 online_data: GuiEmit):

        websocket.enableTrace(True)
        self.status = 'hello'
        self.user_id = user_id
        self.game_instance = game_instance
        self.opponent_instance = opponent_instance
        self.opponent = None
        self.online_lobby_gui = online_lobby
        self.current_waiter_list = []
        self.current_approacher_list = []
        self.ws = websocket.WebSocketApp(
            URLS.mp_server_url,
            on_open=lambda ws: self.on_open(ws),
            on_message=lambda ws, msg: self.on_message(ws, msg),
            on_error=on_error,
            on_close=lambda ws, close_status_code, close_msg: self.on_close(ws, close_status_code, close_msg),
        )
        self.online_data = online_data
        self.ws_thread = threading.Thread(target=self.ws_connect, daemon=True)  # 웹 소켓 연결 스레드
        self.s_game_data_thread = threading.Thread(target=self.s_game_data_loop, daemon=True)  # 게임 데이터 전송 스레드
        self.gui_emit_thread = threading.Thread(target=self.on_emit, daemon=True)  # online_lobby gui 입력 받아옴.

    def on_emit(self):
        while True:
            data = self.online_data.to_handler.get()
            self.parse_emit(data)

    def parse_emit(self, msg: dict):
        todo = msg['t']
        data = msg['d']

        if todo == SCODES['host_accept']:
            self.s_host_accept(data)
        elif todo == SCODES['host_reject']:
            self.s_host_reject(data)
        elif todo == SCODES['approach']:
            self.s_approach(data)
            self.status = 'approaching'
        elif todo == SCODES['approach_cancel']:
            self.s_approach_cancel()
            self.status = 'hello'
        elif todo == SCODES['waiting_list_add']:
            self.s_waiting_list_add()
            self.status = 'waiting'
        elif todo == SCODES['waiting_list_remove']:
            self.s_waiting_list_remove()
            self.status = 'hello'
        elif todo == SCODES['waiting_list_get']:
            self.s_waiting_list_get()

    def on_open(self, ws):
        ws.send(self.user_id)

    def on_message(self, ws, message):
        # print(message)
        try:
            raw_data = json.loads(message)  # 최상위 키가 둘 존재하는 딕셔너리 데이터
            print(raw_data)  # 디버그
        except json.JSONDecodeError:
            raw_data = None
            print('message not in json format')

        if raw_data is not None and raw_data != []:
            self.r_parse_data(raw_data)

    def on_close(self, ws, close_status_code, close_msg):
        print("### closed ###")
        print(f'{close_status_code}')
        print(f'{close_msg}')
        self.online_lobby_gui.on_server_connection_lost()  # 연결 끊어졌을 때 종료창 띄움.

    # 웹소켓 연결
    def ws_connect(self):
        self.ws.run_forever()

    # 게임 인스턴스들 초기화
    def reset_instances(self):
        self.opponent_instance.reset()
        self.game_instance.reset()

    def game_start(self):
        self.status = 'in_game'
        self.reset_instances()
        self.game_instance.status = 'mp_game_ready'
        time.sleep(3)
        self.s_game_data_thread_restart()
        self.game_instance.status = 'in_game'

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

        print(self.status)

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
            self.r_on_lose()  # 패배 화면
        elif t == RCODES['win']:  # 승리
            self.r_on_win()  # 패배 화면
        elif t == RCODES['game_over']:  # 상대 게임 오버
            self.r_on_op_game_over()  # 상대 화면에 게임 오버 띄우기
        elif t == RCODES['match_complete']:  # 매치 끝남
            self.r_on_match_complete()

    def r_update_opponent_info(self, d: dict):
        if d:
            score = d.get('score')
            level = d.get('level')
            goal = d.get('goal')
            matrix = d.get('matrix')
            next_mino_index = d.get('next_mino_index')
            hold_mino_index = d.get('hold_mino_index')

            self.opponent_instance.score = score
            self.opponent_instance.level = level
            self.opponent_instance.goal = goal
            self.opponent_instance.board.temp_matrix = matrix

            self.opponent_instance.next_mino = Mino(next_mino_index)
            if hold_mino_index != -1:
                self.opponent_instance.hold_mino = Mino(hold_mino_index)

    def r_on_lose(self):
        pass

    def r_on_win(self):
        pass

    def r_on_op_game_over(self):
        pass

    def r_on_match_complete(self):
        self.game_instance.status = 'mp_hello'  # todo 게임 인스턴스 상태 상수화
        self.online_lobby_gui.setVisible(True)  # 게임 오버시 gui 다시 보이게

    def r_parse_waiting(self, t, d):
        print(t, d)
        if t == RCODES['approacher_list']:  # 어프로처 리스트
            self.r_update_current_approacher(d)
        elif t == RCODES['waiter_list']:
            self.r_update_current_waiter_list(d)
        elif t == RCODES['game_start']:
            print('game_start!')
            self.game_start()

    def r_update_current_approacher(self, d):
        self.current_approacher_list = d
        self.online_lobby_gui.approacher_list = d  # approacher_list 데이터 수정
        self.online_lobby_gui.approacher_update()  # gui refresh

    def r_parse_approaching(self, t, d):
        if t == RCODES['host_accepted'] or t == RCODES['game_start']:  # 대결 제안 수락됨
            self.game_start()
        elif t == RCODES['host_rejected']:  # 대결 제안 거절됨
            self.r_host_rejected()

    def r_host_rejected(self):
        self.status = 'hello'
        # self.online_lobby_gui.approaching_msg_box.close()

    def r_parse_hello(self, t, d):
        if t == RCODES['waiter_list']:
            self.r_update_current_waiter_list(d)

    def r_update_current_waiter_list(self, d):
        self.current_waiter_list = d
        self.online_lobby_gui.waiter_list = d
        self.online_lobby_gui.waiter_update()  # gui refresh

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

    def s_waiting_list_get(self):
        self.build_and_send_json_req(SCODES['waiting_list_get'])

    def s_approach(self, waiter_id: str):
        self.build_and_send_json_req(SCODES['approach'], waiter_id)

    def s_approach_cancel(self):
        self.build_and_send_json_req(SCODES['approach_cancel'])

    def s_host_accept(self, approacher_id: str):
        self.build_and_send_json_req(SCODES['host_accept'], approacher_id)
        # self.game_start()

    def s_host_reject(self, approacher_id: str):
        self.build_and_send_json_req(SCODES['host_reject'], approacher_id)

    async def s_game_data(self):
        d = {
            'id': self.user_id,
            'score': self.game_instance.score,
            'level': self.game_instance.level,
            'goal': self.game_instance.goal,
            'matrix': self.game_instance.board.temp_matrix,
            'next_mino_index': self.game_instance.next_mino.shape_index,
            'hold_mino_index': self.get_hold_mino_index(),
        }
        self.build_and_send_json_req(SCODES['game_data'], d)

    def get_hold_mino_index(self) -> int:
        if self.game_instance.hold_mino is not None:
            return self.game_instance.hold_mino.shape_index
        else:
            return -1

    def s_game_data_loop(self):  # 스레드로 사용할것
        while True:
            if self.game_instance.status == 'in_game':
                asyncio.run(self.s_game_data())
                time.sleep(0.1)  # 0.1초마다
            if self.game_instance.status == 'game_over':
                self.build_and_send_json_req(t=SCODES['game_over'], d=None)
                break

    def s_game_data_thread_init(self):  # 게임 데이터 전송 스레드 초기화
        self.s_game_data_thread = threading.Thread(target=self.s_game_data_loop, daemon=True)

    def s_game_data_thread_restart(self):  # 게임 데이터 전송 스레드 재시작
        self.s_game_data_thread_init()
        self.s_game_data_thread.start()

