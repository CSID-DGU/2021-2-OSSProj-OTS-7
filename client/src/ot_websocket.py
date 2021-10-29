import websocket
import time
import threading
import json


def on_message(ws, message):
    print(message)


def on_error(ws, error):
    print(error)


def on_close(ws, close_status_code, close_msg):
    print("### closed ###")


def on_open(ws):
    ws.send(json.dumps({'hello': 'server'}))


class OTSWebsocket:
    def __init__(self, user_id, game_instance):
        # websocket.enableTrace(True)
        self.game_instance = game_instance
        self.user_id = user_id
        self.opponent = None
        self.ws = websocket.WebSocketApp(
            f"ws://127.0.0.1:8000/ws/json/{user_id}",
            on_open=on_open,
            on_message=on_message,
            on_error=on_error,
            on_close=on_close,
        )
        self.is_running = False
        self.thread_send_current = threading.Thread(target=self.send_current_json, daemon=True)
        self.is_sending_current = False
        self.is_sending_current_json = False

    def run_forever(self):
        self.is_running = True
        self.ws.run_forever()

    def close(self):
        self.is_running = False
        self.ws.close()

    def send_current(self):
        self.is_sending_current = True

        while self.is_sending_current:
            self.ws.send(str(self.game_instance.score))

            time.sleep(1)

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

    def send_current_json(self):
        self.is_sending_current_json = True
        while self.is_sending_current_json:
            to_send = self.get_current_json()
            self.ws.send(to_send)
            time.sleep(0.5)
