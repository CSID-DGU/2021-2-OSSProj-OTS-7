import websocket
import time
import threading
import json
import pprint




def parse_message(data):
    data_type = data.get('type')
    if data_type == 'solicitor_list':
        pass
    elif data_type == 'match_started':
        pass


def on_error(ws, error):
    print(error)


def on_close(ws, close_status_code, close_msg):
    print("### closed ###")




class OTSWebsocket:
    def __init__(self, user_id, game_instance, multiplayer_instance):
        # websocket.enableTrace(True)
        self.game_instance = game_instance
        self.multiplayer_instance = multiplayer_instance
        self.user_id = user_id
        self.opponent = None
        self.ws = websocket.WebSocketApp(
            f"ws://127.0.0.1:8000/ws",
            on_open=lambda ws: self.on_open(ws),
            on_message=lambda ws, msg: self.on_message(ws, msg),
            on_error=on_error,
            on_close=on_close,
        )
        self.is_running = False
        self.thread = threading.Thread(target=self.loop_thread, daemon=True)
        self.is_sending_current = False
        self.is_sending_current_json = False

    def on_open(self, ws):
        ws.send('a1234')

    def on_message(self, ws, message):
        data = json.loads(message)
        data_type = data[list(data.keys())[0]].get('type')
        if data_type == 'game_data':
            game_data = data[list(data.keys())[0]].get('game_data')
            self.multiplayer_instance.score = game_data.get('score')
            self.multiplayer_instance.level = game_data.get('level')
            self.multiplayer_instance.goal = game_data.get('goal')
            self.multiplayer_instance.board.temp_matrix = game_data.get('matrix')
        pprint.pp(data)
        # parse_message(data)

    def run_forever(self):
        self.is_running = True
        self.ws.run_forever()

    def close(self):
        self.is_running = False
        self.ws.close()

    def send_json_req(self, req):
        self.ws.send(json.dumps(req))

    def add_to_waiting(self):
        req = {
            'type': 'add_to_waiting'
        }
        self.send_json_req(req)

    def solicit(self):
        req = {
            'type': 'solicit',
            'waiter_id': '3456'
        }
        self.send_json_req(req)

    def accept_match(self):
        req = {
            'type': 'accept',
            'solicitor_id': 1234
        }
        self.send_json_req(req)

    def send_current_json(self):
        current_dict = {
            'type': 'game_data',
            'id': self.user_id,
            'opponent': self.opponent,
            'game_data': {
                'score': self.game_instance.score,
                'level': self.game_instance.level,
                'goal': self.game_instance.goal,
                'matrix': self.game_instance.board.temp_matrix,
                # 'next_mino_index': self.game_instance.next_mino.shape_index,
                # 'hold_mino_index': self.game_instance.hold_mino.shape_index
            }
        }
        self.send_json_req(current_dict)

    def loop_thread(self):
        while True:
            if self.game_instance.status == 'in_game':
                self.send_current_json()
            time.sleep(0.1)
