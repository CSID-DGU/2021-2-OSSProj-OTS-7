from .redis_manager import RedisManager
from .user_instance import UserInstance
from .consts import WAITING_CHANNEL
from . import api_requests
SERVER_CODES = {
    'game_data': 'gd',
    'game_over': 'go',
    'match_set': 'ms',
    'game_start': 'gs',
    'host_accepted': 'ha',
    'host_rejected': 'hr',
    'approacher_updated': 'au',
    'match_complete': 'mc',
    'loser': 'lo',
    'winner': 'wi',
    'waiter_list': 'wl'
}

USER_SCODES = {
    'game_data': 'gd',
    'game_over': 'go',
    'waiting_list_add': 'wa',
    'waiting_list_remove': 'wr',
    'waiting_list_get': 'wg',
    'approach': 'a',
    'approach_cancel': 'ac',
    'host_accept': 'ha',
    'host_reject': 'hr',
}

USER_RCODES = {
    'game_data': 'gd',
    'game_over': 'go',
    'match_set': 'ms',  # 현재는 사용할 필요 없음
    'match_complete': 'mc',
    'game_start': 'gs',
    'waiter_list': 'wl',
    'host_accepted': 'ha',
    'host_rejected': 'hr',
    'approacher_list': 'al',
    'lose': 'lo',
    'win': 'wi'
}


def build_dict(data_type, data):
    to_return = {
        't': data_type,
        'd': data
    }
    return to_return


class ServerMsgExecutor:
    def __init__(self, redis_manager: RedisManager):
        self.rdm = redis_manager

    # 서버 명령 실행
    async def server_msg_exec(self, user: UserInstance, msg: dict):
        try:
            mc: str = msg['data']  # 메시지 코드 msg_code
        except (KeyError, TypeError):
            mc = 'error'
            print(f'invalid message data: \n{msg}')

        if mc == SERVER_CODES['game_data']:  # 유저에게 상대의 게임 데이터 전송
            await self.game_data_out(user)
        elif mc == SERVER_CODES['approacher_updated']:  # approachers 정보 갱신
            await self.send_approachers(user)
        elif mc == SERVER_CODES['game_over']:  # 상대방이 게임오버됨.
            await self.op_game_over(user)
        # elif mc == SERVER_CODES['host_accepted']:  # 대결 제안 수락됨.  # 당장은 필요 없어서 각주처리
        #     await self.host_accepted(user)
        elif mc == SERVER_CODES['host_rejected']:  # 대결 제안 거절됨.
            await self.host_rejected(user)
        elif mc == SERVER_CODES['waiter_list']:  # 대기열 전송
            await self.send_waiters(user)
        elif mc == SERVER_CODES['loser'] or mc == SERVER_CODES['winner']:  # 매치 종료
            await self.match_complete(user=user, code=mc)
        elif mc == SERVER_CODES['game_start']:  # 게임 시작됨(대결 제안 수락됨)
            await self.send_start_signal(user)
        else:  # 해당하지 않는 경우 msg_code_map 에 있는 단순 상태 코드만 전송함.
            if mc in SERVER_CODES.values():
                await self.send_user_code(user, mc)

    # 이하 서버 명령으로 실행되는 메소드
    async def game_data_out(self, user: UserInstance):
        op_game_data: dict = await self.rdm.game_data_opponent_get(user.current_match_id, user.player_id)

        if op_game_data is None:  # 매치 시작 직후이거나 네트워크 문제가 있는 등의 상황에서 None 반환 가능
            return

        for val in op_game_data.values():  # 키를 빼고 오브젝트만 전송.
            to_send = build_dict(SERVER_CODES['game_data'], val)
            print(to_send)  # 디버그용
            await user.ws.send_json(to_send)

    # 게임 시작 시그널
    async def send_start_signal(self, user: UserInstance):  # 게임 시작과 동시에 유저 객체에 매치 ID와 상대 정보 저장
        user.set_status_in_game()  # in_game 상태
        user.current_match_id = await self.rdm.match_id_get(user.player_id)  # 유저 객체에 매치 아이디 저장
        user.opponent = await self.rdm.get_opponent(match_id=user.current_match_id, player_id=user.player_id)  # 유저 객체에 상대 아이디 저장
        await self.send_user_code(user, USER_RCODES['game_start'])

    # 상대방 게임 오버
    async def op_game_over(self, user: UserInstance):
        await self.send_user_code(user, USER_RCODES['game_over'])

    # async def host_accepted(self, user: UserInstance):  # 당장은 필요 없어서 각주처리
    #     user.set_status_in_game()
    #     await self.send_user_code(user, USER_RCODES['host_accepted'])

    # 상대가 대결 거절함.
    async def host_rejected(self, user: UserInstance):
        user.init_user()  # 유저 인스턴스 상태 hello 로 변경,
        await self.send_user_code(user, USER_RCODES['host_rejected'])  # approach 거절 코드 전송.

    # 게임 종료, 승패 코드는 메시지 브로커에서 받아서 전달 메시지 브로커 코드와 클라이언트 코드의 win-lose는 같음.
    async def match_complete(self, user: UserInstance, code: str):
        user.init_user()
        await self.rdm.match_id_del([user.player_id])
        await self.send_user_code(user, code)

    # approacher 리스트 전송
    async def send_approachers(self, user: UserInstance):
        approachers = await self.rdm.approacher_get(user.player_id)
        to_send = build_dict(data_type=USER_RCODES['approacher_list'], data=approachers)
        await user.ws.send_json(to_send)

    async def send_waiters(self, user: UserInstance):
        waiters = await self.rdm.waiting_list_get()
        to_send = build_dict(data_type=USER_RCODES['waiter_list'], data=waiters)
        await user.ws.send_json(to_send)

    @staticmethod
    async def send_user_code(user: UserInstance, event_code: str):
        to_send = build_dict(event_code, None)
        await user.ws.send_json(to_send)

    @staticmethod
    async def send_error(user: UserInstance, error_msg: str):
        to_send = build_dict('err', error_msg)
        await user.ws.send_json(to_send)


class UserMsgExecutor:
    def __init__(self, redis_manager: RedisManager):
        self.rdm = redis_manager

    @staticmethod
    async def user_msg_parse(msg):
        try:
            req_type = msg['t']
            req_data = msg['d']
        except (TypeError, KeyError):
            req_type = None
            req_data = None
            print(f'parse request failed \n{msg=}')
        return req_type, req_data

    # 클라이언트 요청 실행
    async def user_msg_exec(self, user: UserInstance, msg: dict):
        t, d = await self.user_msg_parse(msg)
        if t == USER_SCODES['game_data']:  # game data
            await self.game_data_in(user=user, data=d)
        elif t == USER_SCODES['game_over']:  # game_over
            await self.game_over(user=user)
        elif t == USER_SCODES['waiting_list_add']:  # waiting add
            await self.waiting_list_add(user)
        elif t == USER_SCODES['waiting_list_remove']:  # waiting remove
            await self.waiting_list_remove(user)
        elif t == USER_SCODES['approach']:  # approach
            await self.approach(user=user, waiter_id=d)
        elif t == USER_SCODES['approach_cancel']:  # approach cancel
            await self.approach_cancel(user)
        elif t == USER_SCODES['host_accept']:  # host accept
            await self.host_accept(user=user, approacher_id=d)
        elif t == USER_SCODES['host_reject']:  # host reject
            await self.host_reject(user=user, approacher_id=d)
        elif t == USER_SCODES['waiting_list_get']:
            await self.waiting_list_get(user=user)
        else:
            print(f'code {t} is not a valid code')

    # user 게임 오버 신호 수신
    async def game_over(self, user: UserInstance):
        user.status = 'game_over'
        await self.rdm.game_over_user(user.player_id)
        self.rdm.msg_broker.publish(channel=user.opponent, message=SERVER_CODES['game_over'])
        await self.check_match_complete(user)  # 매치 종료 체크

    # 매치 종료 체크, 나중에 게임 오버된 쪽 프로세스가 승패 판별
    async def check_match_complete(self, user: UserInstance):
        winner = await self.rdm.get_game_winner(user.current_match_id)
        if winner is not None:
            await self.publish_result(winner, user)

    async def publish_result(self, winner: str, user: UserInstance):
        for player in [user.player_id, user.opponent]:
            if player == winner:
                self.rdm.msg_broker.publish(player, SERVER_CODES['winner'])
                await api_requests.db_post_winner(player)
            else:
                self.rdm.msg_broker.publish(player, SERVER_CODES['loser'])
                await api_requests.db_post_loser(player)
        await self.rdm.game_session_clear(user.current_match_id)  # 정보 전송 후 레디스에 저장된 세션 정보 삭제

    # 대기열 등록
    async def waiting_list_add(self, user: UserInstance):
        if user.status == 'hello':
            await self.rdm.waiting_list_add(user.player_id)
            self.rdm.msg_broker.publish(WAITING_CHANNEL, '')  # 대기열 업데이트 알림
            user.status = 'waiting'
        else:
            print(f'{user.player_id} is not in hello state. {user.status=}')

    # 대기열 등록 해제
    async def waiting_list_remove(self, user: UserInstance):
        if user.status == 'waiting':
            await self.rdm.waiting_list_remove_and_notice(user.player_id)
            self.rdm.msg_broker.publish(WAITING_CHANNEL, '')
            user.status = 'hello'
        else:
            print(f'{user.player_id} is not in waiting state. {user.status=}')

    # 현재 대기열 전송 요청
    async def waiting_list_get(self, user: UserInstance):
        self.rdm.msg_broker.publish(user.player_id, SERVER_CODES['waiter_list'])

    # 대결 신청
    async def approach(self, user: UserInstance, waiter_id):
        if user.status == 'hello':  # 기본 상태일때
            set_ok: bool = await self.rdm.approacher_set(approacher_id=user.player_id, waiter_id=waiter_id)  # 도전자 등록에 성공하면 True 반환, 실패시 False 반환
            if set_ok:
                user.status = 'approaching'
                user.approached_to = waiter_id
                self.rdm.msg_broker.publish(waiter_id, SERVER_CODES['approacher_updated'])  # waiter 에게 approacher 업데이트 사항을 알림
            else:
                self.rdm.msg_broker.publish(user.player_id, SERVER_CODES['host_rejected'])  # 일단은 요청 거절 메시지 전송.
                print(f'{user.player_id} tried to approach, but failed. The waiter does not exist')  # todo 클라이언트 요청에 대한 에러 전송
        else:
            print(f'{user.player_id} tried to approach, but failed. \nstatus={user.status} \ntarget={waiter_id}')

    # 대결 신청 취소
    async def approach_cancel(self, user: UserInstance):
        if user.status == 'approaching':
            await self.rdm.approacher_del(user.player_id, user.approached_to)  # todo cancel 요청에 상대 id도 포함시키기 (다중 approach)
            user.approached_to = None
            user.status = 'hello'
        else:
            print(f'invalid cancel request. user is not in approaching status. \n{user.player_id=}\n{user.approached_to}')

    # host 요청이 유효한지 판별
    async def is_host_req_valid(self, user: UserInstance, approacher_id):  # host 의 수락, 거절이 유효한지 판별
        if user.status == 'waiting' and approacher_id in await self.rdm.approacher_get(user.player_id):
            return True
        else:
            return False

    # 대결 수락, 게임 시작됨.
    async def host_accept(self, user: UserInstance, approacher_id):
        # redis 에 매치 아이디 저장, 게임 세션 생성, 유저 상태 변경, waiting 리스트에서 유저 제거, 다른 어프로처들에게 거절 신호 보내기, 상대에게 게임 시작 신호 보내기
        if await self.is_host_req_valid(user, approacher_id):
            await self.rdm.match_id_set(approacher_id=approacher_id, host_id=user.player_id)  # redis 에 매치 아이디 저장 (게임 참여자 모두 조회 가능)
            await self.rdm.game_session_set(match_id=user.player_id, player1=user.player_id, player2=approacher_id)  # 게임 세션 생성
            user.status = 'in_game'  # 유저 상태 변경
            self.rdm.msg_broker.publish(channel=approacher_id, message=SERVER_CODES['game_start'])  # 수락한 상대에게 게임 시작 신호
            self.rdm.msg_broker.publish(channel=user.player_id, message=SERVER_CODES['game_start'])  # 플레이어에게 게임 시작 신호

            await self.rdm.waiting_list_remove_and_notice(user.player_id)  # 다른 어프로처들에게 거절 신호 보내기

    # 대결 거절.
    async def host_reject(self, user: UserInstance, approacher_id):  # 대결 거절
        if await self.is_host_req_valid(user, approacher_id):
            self.rdm.msg_broker.publish(channel=approacher_id, message=SERVER_CODES['host_rejected'])  # 거절 신호 publish, sme 쪽에서 상대 유저 상대 상태 변경함.
            await self.rdm.approacher_del(approacher_id, user.player_id)
            self.rdm.msg_broker.publish(channel=user.player_id, message=SERVER_CODES['approacher_updated'])  # 갱신된 approacher 목록 플레이어에게 전송

    # 클라이언트의 게임 데이터를 레디스에 저장
    async def game_data_in(self, user: UserInstance, data: dict):
        if user.current_match_id is None:
            user.current_match_id = await self.rdm.match_id_get(user.player_id)
        if user.opponent is None:
            user.opponent = await self.rdm.get_opponent(user.current_match_id, user.player_id)
        await self.rdm.game_session_data_set(user.current_match_id, user.player_id, data)
        self.rdm.msg_broker.publish(user.opponent, SERVER_CODES['game_data'])
