import redis.exceptions
from rejson import Client, Path
from fastapi import WebSocket
import pickle
import threading


def get_waiting_obj(waiting_player_id: str):  # redis 에 등록할 waiting json
    to_return = {
        'waiter': waiting_player_id,
        'solicitors': [],
    }
    return to_return


def get_session_obj(player1: str, player2: str):  # redis 에 등록할 session json
    to_return = {
        player1: {},
        player2: {},
        'status': 'ready',
    }
    return to_return


class MultiplayerManager:
    def __init__(self, redis_host: str = 'rj', redis_port: int = 6379):
        self.host = redis_host
        self.port = redis_port
        self.session = Client(host=self.host, port=self.port, db=0, decode_responses=True)
        self.waiting = Client(host=self.host, port=self.port, db=1, decode_responses=True)
        self.connections = Client(host=self.host, port=self.port, db=3)

    async def is_waiter_exist(self, waiter_id: str) -> bool:
        if self.waiting.jsonget(waiter_id, Path.rootPath()) is None:
            return False
        else:
            return True

    async def add_to_waiting_list(self, player_id: str):
        obj = get_waiting_obj(player_id)
        self.waiting.jsonset(player_id, Path.rootPath(), obj)

    async def remove_from_waiting_list(self, player_id: str):
        try:
            self.waiting.jsondel(player_id)
        except redis.exceptions.DataError:
            pass

    async def get_solicitors(self, waiter_id):
        return self.waiting.jsonget(waiter_id, Path('.solicitors'))

    async def solicit(self, solicitor_id: str, waiter_id: str):
        solicitors = await self.get_solicitors(waiter_id=waiter_id)
        if solicitor_id not in solicitors:
            self.waiting.jsonarrappend(solicitor_id)

    async def set_match_id(self, player1: str, player2: str):
        self.session.jsonset('opponent', Path(f'.{player1}'), player2)
        self.session.jsonset('opponent', Path(f'.{player2}'), player2)

    async def get_match_id(self, player_id: str):
        return self.session.jsonget('opponent', Path(f'.{player_id}'))

    async def clear_match_id(self, player_id: str):
        self.session.jsondel('opponent', Path(f'.{player_id}'))

    async def accept_match(self, solicitor_id: str, waiter_id: str):
        await self.remove_from_waiting_list(waiter_id)
        obj = get_session_obj(solicitor_id, waiter_id)
        match_id = await self.get_match_id(waiter_id)
        self.session.jsonset('match', Path(f'.{match_id}'), obj)
        # TODO pickle 안 먹힘

    async def send_game_data(self, data, target: str):
        # TODO pickle 안 먹힘
        pass

    async def set_session(self, match_id, player1, player2):
        data = {
            player1: {},
            player2: {},
        }
        self.session.jsonset(match_id, Path.rootPath(), data)

    async def update_game_info(self, data, match_id, player_id):
        try:
            self.session.jsonset(player_id, Path(f'.{match_id}'), data)
        except redis.exceptions.ResponseError:
            await self.set_session(match_id, 'a3456', 'a1234')  # 테스트용 예외처리, 실제 서비스에선 수정 필요.

    async def get_game_info(self, match_id):
        return self.session.jsonget(match_id)
