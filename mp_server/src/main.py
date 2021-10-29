from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from typing import List

from mp_server.src import multiplayer_manager, player_connection


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
    player_instance = player_connection.PlayerConnection(player_id)

    try:
        while True:
            data = await websocket.receive_json()
            player_instance.parse_data(data)

    except WebSocketDisconnect:
        player_id = con_manager.active_connection_dict.get(websocket)
        await mp_manager.clear_match_id(player_id)
        await mp_manager.remove_from_waiting_list(player_id)
        pass
        con_manager.disconnect(websocket)
