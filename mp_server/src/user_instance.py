from .redis_manager import RedisManager
from fastapi import WebSocket

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


class ServerMsgExecutor:
    pass


class UserMsgExecutor:
    def __init__(self, user_id):
        pass

    def exec(self, msg):
        pass

    pass


async def user_msg_parse(msg):
    try:
        req_type = msg['t']
        req_data = msg['d']
    except KeyError:
        req_type = None
        req_data = None
        print(f'parse request failed \n{msg=}')
    return req_type, req_data

# 서버(메시지 브로커) 명령 파싱
async def server_msg_parse(msg):
    pass


class UserInstance:  # 명령 실행 전 상태확인 등 게임 제어
    def __init__(self, player_id: str, mp_manager: RedisManager, websocket: WebSocket):
        self.status = 'hello'
        self.player_id = player_id
        self.mpm = mp_manager
        self.ws = websocket

        self.host = None
        self.opponent = None
        self.current_match_id = None

    # 클라이언트 요청 실행
    async def user_msg_exec(self, msg: dict):
        t, d = user_msg_parse(msg)
        if t == 'gd':  # game data
            await self.game_data_in(data=d)
        elif t == 'wa':  # waiting add
            await self.waiting_list_add()
        elif t == 'wr':  # waiting remove
            await self.waiting_list_remove()
        elif t == 'a':  # approach
            await self.approach(waiter_id=d)
        elif t == 'ac':  # approach cancel
            await self.approach_cancel()
        elif t == 'ha':  # host accept
            await self.host_accept(approacher_id=d)
        elif t == 'hr':  # host reject
            await self.host_reject(approacher_id=d)
        else:
            print(f'code {t} is not a valid code')

    # 이하 클라이언트 요청으로 실행되는 메소드
    async def waiting_list_add(self):
        if self.status == 'hello':
            await self.mpm.waiting_list_add(self.player_id)
            self.status = 'waiting'
        else:
            print(f'{self.player_id} is not in hello state. {self.status=}')

    async def waiting_list_remove(self):
        if self.status == 'waiting':
            await self.mpm.waiting_list_remove(self.player_id)
            self.status = 'hello'
        else:
            print(f'{self.player_id} is not in waiting state. {self.status=}')

    async def approach(self, waiter_id):
        if self.status == 'hello':
            await self.mpm.approacher_set(approacher_id=self.player_id, waiter_id=waiter_id)
            self.status = 'approaching'
            self.host = waiter_id
        else:
            print(f'{self.player_id} tried approach, but failed. \nstatus={self.status} \ntarget={waiter_id}')

    async def approach_cancel(self):
        if self.status == 'approaching':
            pass

    async def host_accept(self, approacher_id):
        if self.status == 'waiting' and approacher_id in self.mpm.approacher_get(self.player_id):
            pass

    async def host_reject(self, approacher_id):
        pass

    # 클라이언트의 send_current_gd 에 대응
    async def game_data_in(self, data: dict):
        pass

    # ############################################

    # 서버 명령 실행
    async def server_msg_exec(self, msg: dict):
        try:
            mc: bytes = msg['data']  # 메시지 코드 msg_code
        except KeyError:
            mc = b'error'
            print(f'invalid message data: \n{msg}')

        if mc == b'gd':
            await self.game_data_out()  # 현재 게임 상황 전송
        elif mc == b'ss':
            await self.send_approachers()  # 현재 approacher 목록 전송
        else:  # 해당하지 않는 경우 msg_code_map 에 있는 단순 상태 코드만 전송함.
            try:
                val = msg_code_map[mc]
                await self.send_event(val)
            except KeyError:
                print(f'invalid code: {mc=}')

    # 이하 서버 명령으로 실행되는 메소드
    async def game_data_out(self):
        if self.current_match_id is None:
            self.current_match_id = self.mpm.player_match_id_get(player_id=self.player_id)
        op_game_data: dict = await self.mpm.game_data_opponent_get(self.current_match_id, self.player_id)
        for val in op_game_data.values():
            to_send = {
                't': 'gd',
                'd': val
            }
            await self.ws.send_json(to_send)

    async def send_event(self, event_code: str):
        to_send = {
            't': event_code,
            'd': None
        }
        await self.ws.send_json(to_send)

    async def send_error(self, error_msg: str):
        to_send = {
            't': 'er',
            'd': error_msg
        }
        await self.ws.send_json(to_send)

    async def send_approachers(self):
        await self.mpm.approacher_get(self.player_id)

