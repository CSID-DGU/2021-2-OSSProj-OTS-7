from .multiplayer_manager import MultiplayerManager

class PlayerConnection:
    def __init__(self, user_id: str, websocket, mp_manager: MultiplayerManager):
        self.status = 'hello'
        self.user_id = user_id
        self.mpm = mp_manager

    async def void_req(self, func, **kwargs):
        await func(**kwargs)
        return 'ok'

    async def parse_request(self, data: dict, player_id: str):
        req_type = data.get('type')
        waiter_id = data.get('waiter_id')
        solicitor_id = data.get('solicitor_id')

        if req_type == 'add_to_waiting':
            await self.void_req(self.mpm.add_to_waiting_list, player_id=player_id)
            return 'ok'
        if req_type == 'add_to_waiting':
            await self.mpm.add_to_waiting_list(player_id=player_id)
            return 'ok'
        elif req_type == 'quit_waiting':
            await self.mpm.remove_from_waiting_list(player_id=player_id)
            return 'ok'
        elif req_type == 'solicit':
            if waiter_id is not None:
                await self.mpm.solicit(player_id, waiter_id=waiter_id)
                return 'ok'
        elif req_type == 'get_solicitors':
            solicitors = await self.mpm.get_solicitors(player_id)
            return solicitors
        elif req_type == 'accept':
            await self.mpm.accept_match(solicitor_id=solicitor_id, waiter_id=self.user_id)
            return 'ok'
