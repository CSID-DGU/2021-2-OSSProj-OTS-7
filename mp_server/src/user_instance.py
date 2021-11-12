from fastapi import WebSocket


class UserInstance:
    def __init__(self, player_id: str, websocket: WebSocket):
        self.status = 'hello'
        self.player_id = player_id
        self.ws = websocket

        self.approached_to = None
        self.opponent = None
        self.current_match_id = None
