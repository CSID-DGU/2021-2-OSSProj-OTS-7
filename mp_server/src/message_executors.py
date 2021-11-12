from .redis_manager import RedisManager
from .user_instance import UserInstance

msg_code_map = {
    b'go': 'go',
    b'ms': 'ms',
    b'mc': 'mc',
    b'gs': 'gs',
    b'sa': 'sa',
    b'su': 'su',
    b'sr': 'sr',
    b'lo': 'lo',
    b'wi': 'wi',
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
    pass

    # 서버 명령 실행
    async def server_msg_exec(self, user: UserInstance, msg: dict):
        try:
            mc: bytes = msg['data']  # 메시지 코드 msg_code
        except KeyError:
            mc = b'error'
            print(f'invalid message data: \n{msg}')

        if mc == b'gd':
            await self.game_data_out(user)  # 현재 게임 상황 전송
        elif mc == b'ss':
            await self.send_approachers(user)  # 현재 approacher 목록 전송
        else:  # 해당하지 않는 경우 msg_code_map 에 있는 단순 상태 코드만 전송함.
            try:
                val = msg_code_map[mc]
                await self.send_event(user, val)
            except KeyError:
                print(f'invalid code: {mc=}')

    # 서버(메시지 브로커) 명령 파싱
    @staticmethod
    async def server_msg_parse(msg):
        pass

    # 이하 서버 명령으로 실행되는 메소드
    async def game_data_out(self, user: UserInstance):
        if user.current_match_id is None:
            user.current_match_id = self.rdm.player_match_id_get(player_id=user.player_id)
        op_game_data: dict = await self.rdm.game_data_opponent_get(user.current_match_id, user.player_id)
        for val in op_game_data.values():
            to_send = build_dict('gd', val)
            await user.ws.send_json(to_send)

    async def send_approachers(self, user: UserInstance):
        await self.rdm.approacher_get(user.player_id)

    @staticmethod
    async def send_event(user: UserInstance, event_code: str):
        to_send = build_dict(event_code, None)
        await user.ws.send_json(to_send)

    @staticmethod
    async def send_error(user: UserInstance, error_msg: str):
        to_send = build_dict('err', error_msg)
        await user.ws.send_json(to_send)


class UserMsgExecutor:
    def __init__(self, redis_manager: RedisManager):
        self.rdm = redis_manager
        pass

    @staticmethod
    async def user_msg_parse(msg):
        try:
            req_type = msg['t']
            req_data = msg['d']
        except KeyError:
            req_type = None
            req_data = None
            print(f'parse request failed \n{msg=}')
        return req_type, req_data

    # 클라이언트 요청 실행
    async def user_msg_exec(self, user: UserInstance, msg: dict):
        t, d = self.user_msg_parse(msg)
        if t == 'gd':  # game data
            await self.game_data_in(user=user, data=d)
        elif t == 'wa':  # waiting add
            await self.waiting_list_add(user)
        elif t == 'wr':  # waiting remove
            await self.waiting_list_remove(user)
        elif t == 'a':  # approach
            await self.approach(user=user, waiter_id=d)
        elif t == 'ac':  # approach cancel
            await self.approach_cancel(user)
        elif t == 'ha':  # host accept
            await self.host_accept(user=user, approacher_id=d)
        elif t == 'hr':  # host reject
            await self.host_reject(user=user, approacher_id=d)
        else:
            print(f'code {t} is not a valid code')

    async def waiting_list_add(self, user: UserInstance):
        if user.status == 'hello':
            await self.rdm.waiting_list_add(user.player_id)
            user.status = 'waiting'
        else:
            print(f'{user.player_id} is not in hello state. {user.status=}')

    async def waiting_list_remove(self, user: UserInstance):
        if user.status == 'waiting':
            await self.rdm.waiting_list_remove(user.player_id)
            user.status = 'hello'
        else:
            print(f'{user.player_id} is not in waiting state. {user.status=}')

    async def approach(self, user: UserInstance, waiter_id):
        if user.status == 'hello':
            await self.rdm.approacher_set(approacher_id=user.player_id, waiter_id=waiter_id)
            user.status = 'approaching'
            user.host = waiter_id
        else:
            print(f'{user.player_id} tried approach, but failed. \nstatus={user.status} \ntarget={waiter_id}')

    async def approach_cancel(self, user: UserInstance):
        if user.status == 'approaching':
            pass

    async def host_accept(self, user: UserInstance, approacher_id):
        if user.status == 'waiting' and approacher_id in self.rdm.approacher_get(user.player_id):
            pass

    async def host_reject(self, user: UserInstance, approacher_id):
        pass

    # 클라이언트의 send_current_gd 에 대응
    async def game_data_in(self, user: UserInstance, data: dict):
        pass
