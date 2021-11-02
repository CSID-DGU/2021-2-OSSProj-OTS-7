import time

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
    def __init__(self, redis_host: str = '192.168.50.125', redis_port: int = 6379):
        self.host = redis_host
        self.port = redis_port
        self.session = Client(host=self.host, port=self.port, db=0, decode_responses=True)  # 게임 세션 데이터 저장
        self.waiting = Client(host=self.host, port=self.port, db=1, decode_responses=True)  # 게임 대기열
        self.msg_broker = Client(host=self.host, port=self.port, db=3, decode_responses=True)  # 메시지 브로커
        self.redis_pup_sub = self.msg_broker.pubsub()  # 메시지 브로커 pub_sub

        self.initial_subscribe()  # 메시지 채널 구독

    # 레디스 메시지 채널 구독
    def initial_subscribe(self):
        to_subscribe = ['waiting']
        self.redis_pup_sub.subscribe(to_subscribe)

    def is_waiter_exist(self, waiter_id: str) -> bool:
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
            self.msg_broker.publish(waiter_id, '{"todo": "su"}')

    async def match_id_set(self, player1: str, player2: str):
        self.session.jsonset('opponent', Path(f'.{player1}'), player2)
        self.session.jsonset('opponent', Path(f'.{player2}'), player2)

    async def player_match_id_get(self, player_id: str):
        return self.session.jsonget('opponent', Path(f'.{player_id}'))

    async def player_match_id_clear(self, player_id: str):
        self.session.jsondel('opponent', Path(f'.{player_id}'))

    async def solicitor_accept(self, solicitor_id: str, waiter_id: str):  # 제안 수락
        self.waiting.jsondel(solicitor_id)
        self.waiting.jsondel(waiter_id)
        await self.match_id_set(solicitor_id, waiter_id)
        await self.game_session_set(match_id=waiter_id, player1=solicitor_id, player2=waiter_id)
        self.msg_broker.publish(solicitor_id, '{"todo": "sa"}')
        self.msg_broker.publish(waiter_id, '{"todo": "sa"}')
        time.sleep(3)
        self.msg_broker.publish(solicitor_id, '{"todo": "gs"}')
        self.msg_broker.publish(waiter_id, '{"todo": "gs"}')

    async def game_session_set(self, match_id, player1, player2):  # 게임 세션 생성
        data = {
            player1: {},
            player2: {},
        }
        self.session.jsonset(match_id, Path.rootPath(), data)

    async def game_session_data_set(self, data, match_id, player_id):  # 게임 데이터 클라이언트에게 받아서 보냄
        try:
            data_to_put = data.get('game_data')
            self.session.jsonset(match_id, Path(f'.{player_id}'), data_to_put)
        except redis.exceptions.ResponseError:
            await self.game_session_set(match_id, 'a3456', 'a1234')  # 테스트용 예외처리, 실제 서비스에선 수정 필요.

    async def game_data_opponent_get(self, match_id, player_id):  # 상대방 게임 정보만 보냄
        raw = self.session.jsonget(match_id)

        raw.pop(player_id)  # 자신 데이터만 뺌
        return raw

    async def game_session_clear(self, match_id):
        pass