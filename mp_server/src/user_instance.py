from fastapi import WebSocket


class UserInstance:  # 명령 실행 전 상태확인 등 게임 제어
    def __init__(self, player_id: str, websocket: WebSocket):
        self.status = 'hello'
        self.player_id = player_id
        self.ws = websocket

        self.host = None
        self.opponent = None
        self.current_match_id = None
