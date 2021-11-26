from . import config, consts
import redis.exceptions
from rejson import Client, Path


def get_waiting_obj(waiting_player_id: str):  # redis 에 등록할 waiting json
    to_return = {
        'waiter': waiting_player_id,
        'approachers': {},
    }
    return to_return


def get_session_obj(player1: str, player2: str):  # redis 에 등록할 session json
    to_return = {
        player1: {},
        player2: {},
        'status': 'ready',
    }
    return to_return


class RedisManager:
    # redis_host 는 ip 주소나 도메인 이름. rj 는 도커 네트워크 상에서의 이름. 도커 네트워크 안에서는 이름으로 호출 가능
    def __init__(self, redis_host: str = config.REDIS_HOST, redis_port: int = config.REDIS_PORT):
        self.host = redis_host
        self.port = redis_port
        self.session = Client(host=self.host, port=self.port, db=0, decode_responses=True)  # 게임 세션 데이터 저장
        self.waiting = Client(host=self.host, port=self.port, db=1, decode_responses=True)  # 게임 대기열
        self.match_ids = Client(host=self.host, port=self.port, db=2, decode_responses=True)
        self.msg_broker = Client(host=self.host, port=self.port, db=3, decode_responses=True)  # 메시지 브로커
        self.msg_pubsub = self.msg_broker.pubsub()  # 메시지 브로커 pub_sub

        self.initial_subscribe()  # 메시지 채널 구독

    # 레디스 메시지 채널 구독
    def initial_subscribe(self):
        to_subscribe = [consts.WAITING_CHANNEL]  # test
        self.msg_pubsub.subscribe(to_subscribe)

    async def waiting_list_get(self) -> list:
        return self.waiting.keys()

    async def waiting_list_add(self, player_id: str):
        obj = get_waiting_obj(player_id)
        self.waiting.jsonset(player_id, Path.rootPath(), obj)

    async def waiting_list_remove(self, player_id: str):
        try:
            self.waiting.jsondel(player_id)
        except redis.exceptions.DataError:
            print(f'{player_id} is not ins waiting list')

    async def approacher_get(self, waiter_id) -> list:
        return self.waiting.jsonobjkeys(waiter_id, '.approachers')

    async def approacher_set(self, approacher_id: str, waiter_id: str) -> bool:
        try:
            self.waiting.jsonset(name=waiter_id, path=f'.approachers.{approacher_id}', obj='')  # redis.exceptions.ResponseError 방지
            return True
        except redis.exceptions.ResponseError:
            return False

    async def approacher_del(self, approacher_id: str, waiter_id: str):
        self.waiting.jsondel(name=waiter_id, path=f'.approachers.{approacher_id}')

    async def waiting_list_remove_and_notice(self, waiter_id):
        try:
            approachers: list = self.waiting.jsonobjkeys(name=waiter_id, path='.approachers')
            if approachers:
                for approacher in approachers:
                    self.msg_broker.publish(channel=approacher, message='hr')  # todo 상수
        except redis.exceptions.ResponseError or redis.exceptions.DataError:
            print(f'redis response|data error! approacher_clear_and_notice({waiter_id=})')
        finally:
            self.waiting.jsondel(name=waiter_id)

    async def match_id_set(self, approacher_id: str, host_id: str):  # 매치 id 는 waiter_id, db 업데이트 등 게임 결과 상태 처리는 waiter 쪽 프로세스가 전담.
        self.match_ids.set(approacher_id, host_id)
        self.match_ids.set(host_id, host_id)

    async def match_id_del(self, players: list):
        for player in players:
            self.match_ids.delete(player)

    async def match_id_get(self, player_id: str) -> str:  # 플레이어의 매치 id 반환
        return self.match_ids.get(player_id)

    async def player_match_id_clear(self, player_id: str):  # 플레이어에게 할당된 매치 id 제거
        self.match_ids.delete(player_id)

    async def game_session_set(self, match_id, player1, player2):  # 게임 세션 생성, waiter 쪽 워커가 처리
        data = {
            player1: {},
            player2: {},
            'game_over': {}
        }
        self.session.jsonset(match_id, Path.rootPath(), data)

    async def get_opponent(self, match_id: str, player_id: str) -> str:
        session_keys: list = self.session.jsonobjkeys(match_id, Path.rootPath())
        session_keys.remove(player_id)
        session_keys.remove('game_over')
        opponent = session_keys[0]
        return opponent

    async def get_game_over(self, match_id) -> list:  # 게임 오버된 유저 리스트 반환
        return self.session.jsonobjkeys(match_id, '.game_over')

    async def game_over_user(self, player_id: str):
        match_id = await self.match_id_get(player_id)
        self.session.jsonset(match_id, f'.game_over.{player_id}', 1)  # match_id.game_over.player_id = 1

    async def get_game_winner(self, match_id) -> (None, str):
        if len(await self.get_game_over(match_id)) < 2:  # 게임 오버된 플레이어 리스트 크기가 2 미만일 경우. 2인 플레이 기준.
            return None  # 게임이 아직 안 끝남.

        session_info: dict = self.session.jsonget(match_id)
        session_info.pop('game_over')
        players = []
        scores = []

        for key in session_info.keys():
            players.append(key)
            scores.append(session_info[key]['score'])
        if scores[0] > scores[1]:
            return players[0]
        else:
            return players[1]

    async def game_session_data_set(self, match_id, player_id, data):  # 게임 데이터 클라이언트에게 받아서 Redis 에 저장
        try:
            if data:
                self.session.jsonset(name=match_id, path=f'.{player_id}', obj=data)
            else:
                print(f'Invalid game data {data=}')
        except redis.exceptions.ResponseError:
            print(f'game session data set failed. \n{player_id=}\n{match_id=}\n{data=}')

    async def game_data_opponent_get(self, match_id, player_id) -> dict:  # 상대방 게임 정보만 return
        raw = self.session.jsonget(match_id)
        raw.pop(player_id)  # 자신 데이터만 뺌
        return raw

    async def game_session_clear(self, match_id: str):
        self.session.delete(match_id)

    async def user_connection_closed(self, player_id):
        p_match_id = await self.match_id_get(player_id)  # 매치 아이디
        if p_match_id is not None:  # 현재 게임중인지 확인
            op_id = await self.get_opponent(p_match_id, player_id)  # 상대 id 확인
            self.msg_broker.publish(channel=op_id, message='go')  # 게임중인 상대에게 게임 오버 신호 보내기 todo 상수 참조
            await self.player_match_id_clear(player_id)  # 플레이어에게 할당된 매치 아이디 제거
        await self.waiting_list_remove_and_notice(player_id)  # 대기중이었을 경우 approacher 들에게 알림.

        # todo approach 한 대상의 approacher 리스트에서 제거
