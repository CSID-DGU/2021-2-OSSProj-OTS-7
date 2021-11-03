from .multiplayer_manager import MultiplayerManager
from fastapi import WebSocket


class PlayerConnection:
    def __init__(self, player_id: str, mp_manager: MultiplayerManager, websocket: WebSocket):
        self.status = 'hello'
        self.player_id = player_id
        self.mpm = mp_manager
        self.ws = websocket

        self.current_match_id = None

    # 이하 요청 수신
    async def parse_request(self, data: dict):
        req_type = data.get('type')
        waiter_id = data.get('waiter_id')
        solicitor_id = data.get('solicitor_id')
        opponent_id = data.get('opponent')
        game_data = data.get('game_data')

        if req_type == 'game_data':
            if self.status == 'in_game':
                await self.mpm.game_session_data_set(data=game_data, match_id=self.current_match_id, player_id=self.player_id)
        elif req_type == 'add_to_waiting':
            self.status = 'waiting'
            await self.mpm.waiting_list_add(player_id=self.player_id)
        elif req_type == 'quit_waiting':
            self.status = 'hello'
            await self.mpm.waiting_list_remove(player_id=self.player_id)
        elif req_type == 'solicit':
            if waiter_id is not None:
                self.status = 'soliciting'
                await self.mpm.solicitor_set(solicitor_id=self.player_id, waiter_id=waiter_id)
        elif req_type == 'get_solicitors':
            solicitors = await self.mpm.solicitor_get(waiter_id=self.player_id)
            return solicitors
        elif req_type == 'accept':
            self.status = 'match_accepted'
            await self.mpm.solicitor_accept(solicitor_id=solicitor_id, waiter_id=self.player_id)

    # 이하 데이터 전송
    async def send_game_info(self):
        if self.current_match_id is None:
            self.current_match_id = self.mpm.player_match_id_get(player_id=self.player_id)
        await self.ws.send_json(await self.mpm.game_data_opponent_get(self.current_match_id, self.player_id))

    async def send_event(self, event_code: str):
        to_send = {
            'type': event_code,
        }
        await self.ws.send_json(to_send)

    async def send_error(self, error_msg):
        to_send = {
            'error': error_msg
        }
        await self.ws.send_json(to_send)

    async def send_solicitors(self):
        await self.mpm.solicitor_get(self.player_id)
