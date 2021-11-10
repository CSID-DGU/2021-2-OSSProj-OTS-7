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

        self.solicitee = None
        self.opponent = None
        self.current_match_id = None

    # 클라이언트 요청 실행
    async def user_msg_exec(self, msg: dict):
        t, d = user_msg_parse(msg)
        if t == 'gd':
            await self.game_data_in(data=d)
        elif t == 'wla':
            await self.waiting_list_add()
        elif t == 'wlr':
            await self.waiting_list_remove()
        elif t == 'sc':
            await self.solicit(waiter_id=d)
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

    async def solicit(self, waiter_id):
        if self.status == 'hello' or self.status == 'waiting':
            await self.mpm.solicitor_set(solicitor_id=self.player_id, waiter_id=waiter_id)
            self.status = 'soliciting'
            self.solicitee = waiter_id
        else:
            print(f'{self.player_id} tried solicit, but failed. \nstatus={self.status} \ntarget={waiter_id}')

    async def solicit_cancel(self):
        if self.status == 'soliciting':
            pass

    async def solicitee_accept(self):
        pass

    async def solicitee_reject(self):
        pass

    async def game_data_in(self, data: dict):
        pass

    # 서버 명령 실행
    async def server_msg_exec(self, msg: dict):
        try:
            msg_code: bytes = msg['data']  # 명령 코드
        except KeyError:
            msg_code = b'error'
            print(f'invalid message data: \n{msg}')

        if msg_code == b'gd':
            await self.game_data_out()  # 현재 게임 상황 전송
        elif msg_code == b'ss':
            await self.send_solicitors()  # 현재 solicitor 목록 전송
        else:  # 해당하지 않는 경우 msg_code_map 에 있는 단순 상태 코드만 전송함.
            try:
                val = msg_code_map[msg_code]
                await self.send_event(val)
            except KeyError:
                print(f'invalid code: {msg_code=}')

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

    async def send_solicitors(self):
        await self.mpm.solicitor_get(self.player_id)

