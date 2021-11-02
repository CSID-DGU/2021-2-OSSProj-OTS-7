import redis.exceptions
from rejson import Client, Path


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
    # redis_host 는 ip 주소나 도메인 이름. rj 는 도커 네트워크 상에서의 이름. 도커 네트워크 안에서는 이름으로 호출 가능
    def __init__(self, redis_host: str = 'rj', redis_port: int = 6379):
        self.host = redis_host
        self.port = redis_port
        self.session = Client(host=self.host, port=self.port, db=0, decode_responses=True)  # 게임 세션 데이터 저장
        self.waiting = Client(host=self.host, port=self.port, db=1, decode_responses=True)  # 게임 대기열

    async def is_waiter_exist(self, waiter_id: str) -> bool:
        if self.waiting.jsonget(waiter_id, Path.rootPath()) is None:
            return False
        else:
            return True

    async def waiting_list_add(self, player_id: str):
        obj = get_waiting_obj(player_id)
        self.waiting.jsonset(player_id, Path.rootPath(), obj)

    async def waiting_list_remove(self, player_id: str):
        try:
            self.waiting.jsondel(player_id)
        except redis.exceptions.DataError:
            pass

    async def solicitor_get(self, waiter_id):
        return self.waiting.jsonget(waiter_id, Path('.solicitors'))

    async def solicitor_set(self, solicitor_id: str, waiter_id: str):
        solicitors = await self.solicitor_get(waiter_id=waiter_id)
        if solicitor_id not in solicitors:
            self.waiting.jsonarrappend(solicitor_id)

    async def match_id_set(self, player1: str, player2: str):
        self.session.jsonset('opponent', Path(f'.{player1}'), player2)
        self.session.jsonset('opponent', Path(f'.{player2}'), player2)

    async def match_id_get(self, player_id: str):
        return self.session.jsonget('opponent', Path(f'.{player_id}'))

    async def match_id_clear(self, player_id: str):
        self.session.jsondel('opponent', Path(f'.{player_id}'))

    async def match_accept(self, solicitor_id: str, waiter_id: str):
        await self.waiting_list_remove(waiter_id)
        obj = get_session_obj(solicitor_id, waiter_id)
        match_id = await self.match_id_get(waiter_id)
        self.session.jsonset('match', Path(f'.{match_id}'), obj)
        # TODO pickle 안 먹힘

    async def game_data_send(self, data, target: str):
        # TODO pickle 안 먹힘
        pass

    async def session_set(self, match_id, player1, player2):
        data = {
            player1: {},
            player2: {},
        }
        self.session.jsonset(match_id, Path.rootPath(), data)

    async def session_info_update(self, data, match_id, player_id):
        try:
            data_to_put = data.get('game_data')
            self.session.jsonset(match_id, Path(f'.{player_id}'), data_to_put)
        except redis.exceptions.ResponseError:
            await self.session_set(match_id, 'a3456', 'a1234')  # 테스트용 예외처리, 실제 서비스에선 수정 필요.

    async def session_info_get(self, match_id):
        return self.session.jsonget(match_id)
