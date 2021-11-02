from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from typing import List
from rejson import Client, Path
import multiplayer_manager, player_request_handler


class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.active_connection_dict = {}

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)


app = FastAPI()
con_manager = ConnectionManager()
mp_manager = multiplayer_manager.MultiplayerManager()


@app.websocket("/ws")
async def websocket_connection(websocket: WebSocket):
    await con_manager.connect(websocket)
    player_id = await websocket.receive_text()
    player_instance = player_request_handler.PlayerConnection(player_id, mp_manager)

    await recieve_data(websocket, player_instance)


async def recieve_data(websocket, player_instance):
    try:
        while True:
            pass
            data = await websocket.receive_json()
            match_id = await mp_manager.match_id_get(player_id=player_instance.player_id)  # 매번 레디스에서 불러오지 않도록 캐싱 필요
            await mp_manager.session_info_update(data=data, match_id=match_id, player_id=player_instance.player_id)

            to_send = await mp_manager.session_info_get(match_id=match_id)
            # to_send = player_instance.parse_request(data=data)

            if to_send is not None:
                await websocket.send_json(to_send)

    except WebSocketDisconnect:
        player_id = con_manager.active_connection_dict.get(websocket)
        await mp_manager.match_id_clear(player_id)
        await mp_manager.waiting_list_remove(player_id)
        pass
        con_manager.disconnect(websocket)
