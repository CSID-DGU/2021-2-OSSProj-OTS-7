from fastapi import WebSocket


class UserInstance:
    def __init__(self, player_id: str, websocket: WebSocket):
        self.status = 'hello'
        self.player_id = player_id
        self.ws = websocket

        self.approached_to = None
        self.opponent = None
        self.current_match_id = None

    def set_status_in_game(self):
        self.status = 'in_game'

    def set_status_hello(self):
        self.status = 'hello'

    def set_status_approaching(self):
        self.status = 'approaching'

    def set_status_waiting(self):
        self.status = 'waiting'

    def init_user(self):
        self.set_status_hello()
        self.approached_to = None
        self.opponent = None
        self.current_match_id = None
