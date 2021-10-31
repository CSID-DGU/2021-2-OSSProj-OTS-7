import websocket
import time
import threading
import json
import pprint


def on_message(ws, message):
    data = json.loads(message)
    pprint.pp(data)
    # parse_message(data)


def parse_message(data):
    data_type = data.get('type')
    if data_type == 'solicitor_list':
        pass
    elif data_type == 'game_data':
        pass


def on_error(ws, error):
    print(error)


def on_close(ws, close_status_code, close_msg):
    print("### closed ###")


def on_open(ws):
    ws.send('a1234')


class OTSWebsocket:
    def __init__(self, user_id, game_instance):
        # websocket.enableTrace(True)
        self.game_instance = game_instance
        self.user_id = user_id
        self.opponent = None
        self.ws = websocket.WebSocketApp(
            f"ws://127.0.0.1:8000/ws",
            on_open=on_open,
            on_message=on_message,
            on_error=on_error,
            on_close=on_close,
        )
        self.is_running = False
        self.thread = threading.Thread(target=self.loop_thread, daemon=True)
        self.is_sending_current = False
        self.is_sending_current_json = False

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

    def get_current_json(self):
        current_dict = {
            'id': self.user_id,
            'opponent': self.opponent,
            'score': self.game_instance.score,
            'level': self.game_instance.level,
            'goal': self.game_instance.goal,
            'matrix': self.game_instance.board.temp_matrix,

            # 'next_mino': self.game_instance.next_mino,
            # 'hold_mino': self.game_instance.hold_mino
        }
        return json.dumps(current_dict)

    def loop_thread(self):
        while True:
            if self.game_instance.status == 'in_game':
                to_send = self.get_current_json()
                self.ws.send(to_send)
            time.sleep(0.1)
